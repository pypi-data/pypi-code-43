import click
from . import Model
from sqlalchemy.schema import CreateTable


@click.group()
def main():
    pass


@main.command(name="dump-schema")
def main_dump_schema():
    for table_name, table in Model.metadata.tables.items():
        print(f"{CreateTable(table)};", end="")


if __name__ == "__main__":
    main()
