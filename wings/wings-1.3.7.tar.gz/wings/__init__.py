"""WINGS API Client."""

import configparser
import os
from pathlib import Path

from .api_client import ApiClient


def _locate_creds_file(credentials_file=None):
    if credentials_file:
        credentials_file = Path(credentials_file)
    else:
        credentials_file = Path(os.getenv("WCM_CREDENTIALS_FILE", "~/.wcm/credentials"))

    return credentials_file.expanduser()


def _load_creds(
    server=None,
    export_url=None,
    username=None,
    password=None,
    domain=None,
    credentials_file=None,
    profile=None,
    **kwargs,
):
    wcm_profile = profile or os.getenv("WCM_PROFILE", "default")
    creds_file = _locate_creds_file(credentials_file)
    if Path(creds_file).exists():
        config = configparser.ConfigParser()
        config.read(creds_file)
    else:
        config = {wcm_profile: {}}

    try:
        return {
            "server": (
                server
                or os.getenv("WCM_WINGS_SERVER", config[wcm_profile]["serverWings"])
            ).strip("/"),
            "export_url": (
                export_url
                or os.getenv(
                    "WCM_WINGS_EXPORT_URL", config[wcm_profile]["exportWingsURL"]
                )
            ),
            "username": (
                username or os.getenv("WCM_USER", config[wcm_profile]["userWings"])
            ),
            "domain": (
                domain or os.getenv("WCM_DOMAIN", config[wcm_profile]["domainWings"])
            ),
            "password": (
                password
                or os.getenv("WCM_PASSWORD", config[wcm_profile]["passwordWings"])
            ),
        }
    except KeyError as e:
        key = str(e).strip("'")
        if key == wcm_profile:
            raise ValueError(f"Unable to find credentials for profile <{key}>") from e
        else:
            raise ValueError(
                f"""Unable to find credential attribute <{key}> from,
    CLI Overrides
    Environment Variables
    Credentials file <{creds_file}> under profile <{wcm_profile}>"""
            ) from e


def init(**kwargs):
    """Initialize WINGS API Client.

    Keyword Args:
        server (str): WINGS Server URL
        export_url (str): WINGS Server Export URL
        username (str): Username
        password (str): Password
        domain (str): WINGS Domain
        credentials_file (str): Path to WINGS credentials file.
        profile (str): Profile name to fetch from credentials file.
    """
    _creds = _load_creds(**kwargs)
    return ApiClient(**_creds)
