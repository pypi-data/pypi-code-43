# -*- coding: utf-8 -*-
from publishing_boy.publishing_boy import process
from publishing_boy.process import create_content_folder

"""Console script for publishing_boy."""
import sys
import click


@click.command()
@click.argument('input_folder')
@click.argument('output_folder')
def main(input_folder, output_folder):
    """Console script for publishing_boy."""
    click.echo('Running publishing boy...')
    create_content_folder(output_folder)

    process(input_folder)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
