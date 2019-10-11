import click
import yaml
from yaml import load

from db_anonnymizer.business import connect_to_db


@click.command()
@click.argument('dsn')
@click.argument('config_file')
def tool(dsn, config_file):
    db = connect_to_db(dsn)

    tables = db.tables
    click.echo('SET foreign_key_checks = 0;')
    for table in tables:
        click.echo("-- Create statement for the table {}".format(table.name))
        click.echo(table.create_sql_statement + ';')

        config = load(open(config_file), Loader=yaml.SafeLoader)
        if table.name in config:
            click.echo(
                "-- Generated anonnymous data for the table {}".format(
                    table.name
                )
            )
            data_generator = table.anonymize(config[table.name])
        else:
            click.echo(
                "-- Dump data for the table {}".format(
                    table.name
                )
            )
            data_generator = table.dump()

        for generated_sql in data_generator:
            click.echo(generated_sql)

    click.echo('-- Enable FK checks')
    click.echo('SET foreign_key_checks = 1;')

