from settingscascade.element_schema import ElementSchema
from settingscascade.manager import SettingsManager

__all__ = ("SettingsManager", "ElementSchema")

try:  # pragma: no cover
    import pkg_resources

    try:
        __version__ = pkg_resources.get_distribution("settingscascade").version
    except pkg_resources.DistributionNotFound:
        __version__ = "0.0.0"
except (ImportError, AttributeError):  # pragma: no cover
    __version__ = "0.0.0"
