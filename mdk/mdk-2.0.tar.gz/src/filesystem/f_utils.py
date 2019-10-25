"""file helper functions for mdk"""
import json
import os
from pathlib import Path, PosixPath
import stat
from typing import Any, Dict, List, Union

import yaml
from yaml import SafeDumper


def read_compose_yaml(file_path=Path("./docker-compose.yaml")) -> Union[Dict[str, Any], None]:
    """find docker-compose.yaml in pwd and return its contents (or None if file not found)"""
    return parse_file(file_path, "yaml")


def new_file(
        name: str,
        directory: Path,
        lines: List[str],
        executable=False):
    """generate a new dockerfile"""
    newfile = directory/name
    newfile.write_text("\n".join(lines))

    # see https://stackoverflow.com/a/12792002/11942851
    if executable:
        file_stat = os.stat(newfile)
        os.chmod(newfile, file_stat.st_mode | stat.S_IEXEC)


def parse_file(file_path: Path, file_format: str) -> Union[Dict[str, Any], None]:
    """file reader & parser"""
    if not file_path.is_file():
        return None

    file_data = file_path.read_text()
    if file_format == "yaml":
        parsed_yaml = yaml.load(file_data, Loader=yaml.Loader) # type: Dict[str, Any]
        return parsed_yaml
    if file_format == "json":
        parsed_json = json.loads(file_data) # type: Dict[str, Any]
        return parsed_json
    raise ValueError("tried to parse file with unsupported format {}".format(format))


def path_to_relative_str(path: PosixPath) -> str:
    """transform a posix path to a string path, relative to cwd"""
    relative_posix = path.relative_to(".")
    return str(relative_posix)


def service_to_local_compose(name, config):
    """insert a service into the relative docker-compose.yaml"""
    compose_data = read_compose_yaml()
    if not compose_data:
        raise FileExistsError("could not find local docker-compose.yaml for service initialization")

    if not compose_data["services"]:
        compose_data["services"] = {}
    compose_data["services"][name] = config

    # "None" will not be printed (instead of printing "null")
    SafeDumper.add_representer(
        type(None),
        lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:null', '')
    )
    compose_stream = Path("./docker-compose.yaml").open("w")
    yaml.dump(compose_data, compose_stream, Dumper=SafeDumper)


def touch_local_env():
    """ensure .env file exists in local directory"""
    env_file = Path("./.env")
    env_file.touch()


def user_docker_conf() -> Union[Dict[str, Any], None]:
    """find user's docker info within ~/.docker/config.json"""
    return parse_file(Path.home()/".docker"/"config.json", "json")


def write_compose(
        file_dir: Path,
        content: Dict,
        extension: str = None):
    """write a docker-compose file"""
    compose_file_name = "docker-compose"
    if extension is not None:
        compose_file_name += ".{}".format(extension)
    compose_file_name += ".yaml"

    compose_file_path = file_dir/compose_file_name
    compose_stream = compose_file_path.open("w")
    yaml.dump(content, compose_stream, Dumper=SafeDumper)
