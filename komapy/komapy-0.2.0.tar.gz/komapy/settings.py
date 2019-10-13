"""
KomaPy app settings.
"""

from .constants import TIME_ZONE


class AppSettings:
    """
    A settings object. It defines access to the BMA API using API key or
    access token and other setting parameters.
    """

    api_key = None
    access_token = None
    time_zone = TIME_ZONE
    host = None


app_settings = AppSettings()
