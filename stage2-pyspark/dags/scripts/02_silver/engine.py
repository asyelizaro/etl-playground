import importlib
from pathlib import Path

import yaml


def load_config(config_path: str | None = None):
    if config_path is None:
        config_path = Path(__file__).resolve().parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_table(table_name: str, dt: str | None = None):
    config = load_config()
    tables = config.get("tables", [])

    table_config = next((item for item in tables if item["name"] == table_name), None)
    if table_config is None:
        raise ValueError(f"Table {table_name} not found in config")

    handler_name = table_config.get("handler")
    if not handler_name:
        raise ValueError(f"No handler defined for table {table_name}")

    module_name, function_name = handler_name.rsplit(".", 1)
    module = importlib.import_module(module_name)
    handler = getattr(module, function_name)
    return handler(dt=dt, table_config=table_config)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--table", required=True)
    parser.add_argument("--dt", required=False, default=None)
    args = parser.parse_args()

    run_table(args.table, dt=args.dt)
