import os
from typing import Optional


def set_log_level(log_level: Optional[str] = None):
    """Set log level."""
    import logging

    if not log_level:
        log_level = os.environ.get('LOG_LEVEL', 'INFO')

    log_level = logging.getLevelName(log_level)
    logging.getLogger('base-package').setLevel(log_level)
    os.environ['LOG_LEVEL'] = logging.getLevelName(log_level)


def configure_colored_logging(log_level: Optional[str] = None):
    import coloredlogs

    log_level = log_level or os.environ.get('LOG_LEVEL', 'INFO')

    field_styles = coloredlogs.DEFAULT_FIELD_STYLES.copy()
    field_styles["asctime"] = {}
    level_styles = coloredlogs.DEFAULT_LEVEL_STYLES.copy()
    level_styles["debug"] = {}
    coloredlogs.install(
        level=log_level,
        use_chroot=False,
        fmt="%(asctime)s %(levelname)-8s %(name)s  - %(message)s",
        level_styles=level_styles,
        field_styles=field_styles,
    )
