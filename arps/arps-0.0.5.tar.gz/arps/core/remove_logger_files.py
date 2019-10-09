import os


def remove_logger_files(logger):
    for handler in logger.handlers:
        if hasattr(handler, 'baseFilename'):
            try:
                os.remove(handler.baseFilename)
            except (FileNotFoundError, OSError, PermissionError):
                pass
