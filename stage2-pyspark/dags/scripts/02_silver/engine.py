import importlib
from pathlib import Path

import yaml


def load_config():

    path = Path(__file__).parent / "config.yaml"

    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def run_table(table_name, dt=None):

    config = load_config()

    tables = config["tables"]

    table_config = None

    for table in tables:
        if table["name"] == table_name:
            table_config = table
            break

    if table_config is None:
        raise ValueError(
            f"Table {table_name} not found"
        )


    handler = table_config["handler"]

    module_name, function_name = handler.split(".")


    module = importlib.import_module(module_name)

    function = getattr(
        module,
        function_name
    )


    return function(
        dt=dt,
        table_config=table_config
    ) 