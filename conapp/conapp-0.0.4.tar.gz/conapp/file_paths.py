import os

from datetime import datetime

CONFIG_DIR = os.path.join(
    os.environ.get('XDG_CONFIG_HOME', os.path.expanduser("~/")),
    ".config/conapp"
)
CONFIG_DIR_REPO = "repo"
CONFIG_DIR_SNAPSHOT = "snapshots"


def get_config_dir(dir: str) -> str:
    """Get a directory prefixed in the config dir"""
    return os.path.join(CONFIG_DIR, dir)


CONFIG_DIRS = [
    get_config_dir(CONFIG_DIR_SNAPSHOT),
    get_config_dir(CONFIG_DIR_REPO)
]


# TODO: Abstract repo default into a constant somewhere
def get_repo_dir(user: str, repo: str) -> str:
    return os.path.join(
        get_config_dir(CONFIG_DIR_REPO),
        user,
        repo
    )


def get_snapshot_filename() -> str:
    return os.path.join(
        get_config_dir(CONFIG_DIR_SNAPSHOT),
        datetime.now().strftime("%Y-%m-%d.%H-%M-%S") + ".tar.gz"
    )


def get_snapshot_by_rel(rel: int) -> str:
    """
    get a snapshot filename by rel
    :param rel:
    :return:
    """
    snapshot_dir = get_config_dir(CONFIG_DIR_SNAPSHOT)
    files = os.listdir(snapshot_dir)
    files.sort(reverse=True)

    return os.path.join(
        snapshot_dir,
        files[rel]
    )


def check_dirs(dirs: list = CONFIG_DIRS) -> bool:
    for config_dir in dirs:
        if not os.path.isdir(config_dir):
            return False

    return True


def create_dirs(dirs: list = CONFIG_DIRS) -> None:
    """
    Create the directories required to operate
    """
    for config_dir in dirs:
        try:
            os.makedirs(config_dir)
        except FileExistsError:
            print(f"{config_dir} already exists, not recreating")
            continue
