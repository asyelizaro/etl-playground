from pyspark.sql.functions import col, concat_ws, current_timestamp, lit

from utils import (
    RECORD_SOURCE,
    append_changed_satellite_rows,
    append_new_rows,
    business_key_hash,
    full_table_name,
    get_latest_partition_path,
    get_spark_session,
    hash_diff,
    link_hash,
    resolve_dt,
)


def _read_bronze(spark, table_config, dt):
    source_path = get_latest_partition_path(table_config["source_table"], dt=dt)
    bronze_df = spark.read.parquet(source_path)

    columns_mapping = table_config["columns"]
    return bronze_df.select(
        *[
            col(source_column).alias(target_column)
            for target_column, source_column in columns_mapping.items()
        ]
    )


def load_hub_sat(dt=None, table_config=None):
    spark = get_spark_session(app_name=f"silver-{table_config['name']}")

    try:
        database = table_config["database"]
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {database}")

        dt = resolve_dt(dt)
        business_key = table_config["business_key"]
        hub = table_config["hub"]
        sat = table_config["sat"]
        sat_attributes = sat["attributes"]
        hash_diff_column = sat["hash_diff_column"]

        silver_df = (
            _read_bronze(spark, table_config, dt)
            .dropDuplicates([business_key])
        )

        hub_df = (
            silver_df
            .select(col(business_key))
            .withColumn(hub["key_column"], business_key_hash(business_key))
            .withColumn(hub["load_dt_column"], current_timestamp())
            .withColumn(hub["source_column"], lit(RECORD_SOURCE))
        )

        append_new_rows(
            spark,
            hub_df,
            full_table_name(database, hub["target_table"]),
            hub["key_column"],
        )

        sat_df = (
            silver_df
            .withColumn(hub["key_column"], business_key_hash(business_key))
            .withColumn(hash_diff_column, hash_diff(sat_attributes))
            .select(
                col(hub["key_column"]),
                *[col(attribute) for attribute in sat_attributes],
                col(hash_diff_column),
            )
            .withColumn(sat["load_dt_column"], current_timestamp())
            .withColumn(sat["source_column"], lit(RECORD_SOURCE))
        )

        append_changed_satellite_rows(
            spark,
            sat_df,
            full_table_name(database, sat["target_table"]),
            hub["key_column"],
            hash_diff_column,
            sat["load_dt_column"],
        )

        return True

    finally:
        spark.stop()


def load_link(dt=None, table_config=None):
    spark = get_spark_session(app_name=f"silver-{table_config['name']}")

    try:
        database = table_config["database"]
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {database}")

        dt = resolve_dt(dt)
        link = table_config["link"]
        left_key = link["left_business_key"]
        right_key = link["right_business_key"]

        link_df = (
            _read_bronze(spark, table_config, dt)
            .filter(col(left_key).isNotNull() & col(right_key).isNotNull())
            .dropDuplicates([left_key, right_key])
            .withColumn(link["left_key_column"], business_key_hash(left_key))
            .withColumn(link["right_key_column"], business_key_hash(right_key))
            .withColumn(
                link["key_column"],
                link_hash(link["left_key_column"], link["right_key_column"]),
            )
            .withColumn(link["load_dt_column"], current_timestamp())
            .withColumn(link["source_column"], lit(RECORD_SOURCE))
            .select(
                link["key_column"],
                link["left_key_column"],
                link["right_key_column"],
                link["load_dt_column"],
                link["source_column"],
            )
        )

        append_new_rows(
            spark,
            link_df,
            full_table_name(database, link["target_table"]),
            link["key_column"],
        )

        return True

    finally:
        spark.stop()


def load_link_sat(dt=None, table_config=None):
    spark = get_spark_session(app_name=f"silver-{table_config['name']}")

    try:
        database = table_config["database"]
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {database}")

        dt = resolve_dt(dt)
        link = table_config["link"]
        sat = table_config["sat"]
        left_key = link["left_business_key"]
        right_key = link["right_business_key"]
        sat_attributes = sat["attributes"]
        hash_diff_column = sat["hash_diff_column"]

        bronze_df = _read_bronze(spark, table_config, dt)

        for attribute in sat_attributes:
            if attribute not in bronze_df.columns:
                bronze_df = bronze_df.withColumn(
                    attribute,
                    concat_ws(
                        "-",
                        col(left_key).cast("string"),
                        col(right_key).cast("string"),
                    ),
                )

        link_sat_df = (
            bronze_df
            .filter(col(left_key).isNotNull() & col(right_key).isNotNull())
            .dropDuplicates([left_key, right_key, *sat_attributes])
            .withColumn(link["left_key_column"], business_key_hash(left_key))
            .withColumn(link["right_key_column"], business_key_hash(right_key))
            .withColumn(
                link["key_column"],
                link_hash(link["left_key_column"], link["right_key_column"]),
            )
            .withColumn(hash_diff_column, hash_diff(sat_attributes))
            .select(
                col(link["key_column"]),
                *[col(attribute) for attribute in sat_attributes],
                col(hash_diff_column),
            )
            .withColumn(sat["load_dt_column"], current_timestamp())
            .withColumn(sat["source_column"], lit(RECORD_SOURCE))
        )

        append_changed_satellite_rows(
            spark,
            link_sat_df,
            full_table_name(database, sat["target_table"]),
            link["key_column"],
            hash_diff_column,
            sat["load_dt_column"],
        )

        return True

    finally:
        spark.stop()
