from pathlib import Path


def blyaml_directory() -> Path:
    """The folder to store the sesame token and the cached lists."""
    directory_path = Path.home() / ".blyaml"
    directory_path.mkdir(exist_ok=True)
    return directory_path
