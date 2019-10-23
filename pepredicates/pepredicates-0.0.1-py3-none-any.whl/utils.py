import os

def get_version_information():
    """Grab the version from the .version file
    """
    version_file = os.path.join(
        os.path.dirname(__file__), ".version")

    try:
        with open(version_file, "r") as f:
            f = f.read()
        version = f
    except Exception:
        version = "No version information found"
    return version
