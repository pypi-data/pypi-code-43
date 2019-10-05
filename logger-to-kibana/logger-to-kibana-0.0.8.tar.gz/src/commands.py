"""
This file contains the commands available for the program
"""
import click
import src.file_processor as processor
import src.kibana as kib
from pathlib import Path


@click.group()
def commands():
    """
    Process the file provided according to conditions
    """


@commands.command(
        "process", short_help="Process the folder")
@click.option("--folder", "-f",
              required=False, metavar="str", help="Folder to read")
def process(folder: str):
    print(processor.process_folder(folder))


@commands.command(
    "process_and_generate",
    short_help="Process the folder and generate visualisation"
)
@click.option("--folder", "-f",
              required=False, metavar="str", help="Folder to read")
def process_and_generate(folder: str):
    process_and_generate_visualisations(folder)


@commands.command(
    "process_generate_and_send",
    short_help="Process the folder, generate visualisation and send"
)
@click.option("--folder", "-f",
              required=False, metavar="str", help="Folder to read")
def process_generate_and_send(folder: str):
    process_generate_and_send_visualisations(folder)


def process_and_generate_visualisations(folder: str):
    processed = processor.process_folder(folder)
    print(kib.generate_folder_visualisation(
            get_folder_name(folder), processed))


def process_generate_and_send_visualisations(folder: str):
    processed = processor.process_folder(folder)
    kib.generate_and_send_visualisation(get_folder_name(folder), processed)


def get_folder_name(folder: str) -> str:
    return Path(folder).parts[-1]
