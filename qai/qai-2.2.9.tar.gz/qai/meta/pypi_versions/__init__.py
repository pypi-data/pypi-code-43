from distutils.version import LooseVersion

import requests


def get_pypi_versions():
    r = requests.get("https://pypi.org/pypi/qai/json")
    pypi_versions = list(r.json()["releases"].keys())
    pypi_versions.sort(key=LooseVersion)
    return pypi_versions
