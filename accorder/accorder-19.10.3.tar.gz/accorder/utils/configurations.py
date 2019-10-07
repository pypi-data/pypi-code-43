import os
import click
import urllib
import configparser
from accorder.utils.configs import read_config
from accorder.utils.configs import write_config
from accorder.utils.configs import edit_config
from accorder.utils.configs import check_sections


def run_configuration(app_name, configuration_id, show, replace):
    if configuration_id:
        if show:
            click.echo(click.get_current_context().get_help())
            click.get_current_context().exit()

        req_url = f"https://accorder.memoryoftheworld.org/{configuration_id}"
        req = urllib.request.Request(req_url)
        try:
            res = urllib.request.urlopen(req)
        except Exception as e:
            click.echo("")
            click.echo(f'Download from {req_url} didn\'t work. Please, check if {configuration_id} is correct CONFIGURATION_ID or check your internet connection and try again. Also, this might be the error: "{e}"')
            click.echo("")
            click.get_current_context().exit()

        res_code = res.getcode()
        if res_code == 200:
            config_string = res.read().decode()
        else:
            click.echo("")
            click.echo(f"Download from {req_url} didn't work. Please, check if {configuration_id} is correct or check your internet connection and try again.")
            click.echo("")
            click.get_current_context().exit()

        try:
            parser = configparser.ConfigParser()
            parser.read_string(config_string)
        except Exception as e:
            click.echo("")
            click.echo(f"{req_url} has corrupted configuration file. Check out with the administrator what could be done about that. Good luck! Also, this might be the error: {e}")
            click.echo("")
            click.get_current_context().exit()

        cfg = os.path.join(click.get_app_dir(app_name), "accorder.ini")

        new_sections = []
        for section in parser.sections():
            for option, value in parser.items(section):
                new_sections.append({
                    "section": section,
                    "option": option,
                    "value": value
                })

        if replace:
            with open(cfg, "w") as f:
                f.write(config_string)
        else:
            write_config(app_name, new_sections)
        click.get_current_context().exit()

    if show:
        config = read_config(app_name)
        config_path = os.path.join(click.get_app_dir(app_name), "accorder.ini")
        click.echo(f"CONFIGURATION FILE: {config_path}")
        click.echo("")

        if not config.keys():
            click.echo("")
            click.echo(
                f"{config_path} has no profile configured. First, you probably want to initialize your setup with:\n`accorder configuration CONFIGURATION_ID`\nor if you just want a profile to build a standalone, portable Calibre library run:\n`accorder build PROFILE`"
            )
            click.echo("")

        for profile in config.keys():
            sections = check_sections(config, profile)
            if not sections:
                edit_config(app_name, profile)

            if "calibre" in sections:
                for option in [
                    "librarian",
                    "local_directory",
                    "library_uuid",
                    "library_secret",
                ]:
                    if option not in config[profile]["calibre"]:
                        edit_config(app_name, profile)
            else:
                edit_config(app_name, profile)
            config = read_config(app_name)
            librarian = config[profile]["calibre"]["librarian"]
            local_directory = config[profile]["calibre"]["local_directory"]
            click.echo(f"..PROFILE: {profile}")
            click.echo(f"....LIBRARIAN: {librarian}")
            click.echo(f"....CALIBRE LIBRARY: {local_directory}")

            upload = []
            if "rsync" in sections:
                upload.append("RSYNC")
            if "rclone" in sections:
                upload.append("RCLONE")
            if upload:
                upload = ", ".join(upload)
                click.echo(f"....UPLOAD: {upload}")

            if "motw" in sections:
                motw_url = f'https://{config[profile]["motw"]["subdomain"]}.{config[profile]["motw"]["domain"]}'
                click.echo(f"....SHARED AT: {motw_url}")

            click.echo("")

    if replace and not configuration_id:
        click.echo(click.get_current_context().get_help())
