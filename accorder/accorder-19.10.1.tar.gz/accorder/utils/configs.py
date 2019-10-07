import os
import click
import configparser
import collections
import pathlib
import uuid


def read_config(app_name):
    cfg = os.path.join(click.get_app_dir(app_name), "accorder.ini")
    if not pathlib.Path(cfg).exists():
        click.echo(
            f"{cfg} doesn't exist. First, check out: `accorder configuration --help`."
        )
        click.get_current_context().exit()
    parser = configparser.RawConfigParser()
    parser.read([cfg])
    nested_dict = lambda: collections.defaultdict(nested_dict)
    conf = nested_dict()
    for section in parser.sections():
        profile, context = section.split("_")
        for key, value in parser.items(section):
            conf[profile][context][key] = value
    return conf


def write_config(app_name, options):
    cfg = os.path.join(click.get_app_dir(app_name), "accorder.ini")
    if not pathlib.Path(cfg).exists():
        os.makedirs(click.get_app_dir(app_name), exist_ok=True)

    parser = configparser.ConfigParser()
    parser.read(cfg)
    for option in options:
        if not parser.has_section(option["section"]):
            parser.add_section(option["section"])
        parser.set(option["section"], option["option"], option["value"])
    with open(cfg, "w") as f:
        parser.write(f)


def check_profile(config, profile):
    if profile not in list(config.keys()):
        click.echo(
            f"'{profile}' not found in the list of configured profiles: {', '.join(config.keys())}"
        )
        only_calibre = click.confirm(
            "Do you want to create a profile just for building the standalone, portable Calibre webapp?",
            default=True,
        )
        if not only_calibre:
            click.get_current_context().exit()


def check_sections(config, profile):
    return [
        section
        for section in ["meta", "calibre", "motw", "rsync", "tunnel", "rclone"]
        if section in config[profile].keys()
    ]


def edit_config(app_name, profile, directory=None, librarian=None):
    config = read_config(app_name)
    check_profile(config, profile)

    if "local_directory" not in config[profile]["calibre"]:
        if not directory:
            local_directory = click.prompt(
                f"'Please, provide local Calibre's collection directory for {profile}",
                type=click.Path(exists=True, resolve_path=True, file_okay=False),
            )
        else:
            local_directory = directory
    else:
        if not directory:
            local_directory = config[profile]["calibre"]["local_directory"]
        else:
            local_directory = directory

    if local_directory[:-1] != "/":
        local_directory += "/"

    while "/" * 2 in local_directory:
        local_directory = local_directory.replace("//", "/")

    if not pathlib.Path(f"{local_directory}metadata.db").is_file():
        click.echo(
            f"{local_directory} provided does not point to the root of Calibre library. Please, check again and provide the correct path."
        )
        click.get_current_context().exit()

    new_sections = [
        {
            "section": f"{profile}_calibre",
            "option": "local_directory",
            "value": local_directory,
        }
    ]

    if "librarian" not in config[profile]["calibre"]:
        if not librarian:
            librarian = click.prompt(
                f"'Please, provide librarian's name for {profile} (max. 42 chars)"
            )

    if librarian:
        new_sections.append(
            {
                "section": f"{profile}_calibre",
                "option": "librarian",
                "value": librarian[:48],
            }
        )

    if "library_uuid" not in config[profile]["calibre"]:
        new_sections.append(
            {
                "section": f"{profile}_calibre",
                "option": "library_uuid",
                "value": str(uuid.uuid4()),
            }
        )

    if "library_secret" not in config[profile]["calibre"]:
        new_sections.append(
            {
                "section": f"{profile}_calibre",
                "option": "library_secret",
                "value": uuid.uuid4().hex,
            }
        )

    write_config(app_name, new_sections)

    return read_config(app_name)
