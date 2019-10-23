#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
from service_runner.service_runner.settings import CURRENT_DIR, BASE_DIR
import os
import sys
import shutil


def main():
    if os.path.exists(CURRENT_DIR + '/log'):
        pass
    else:
        os.makedirs(CURRENT_DIR + '/log')

    if os.path.exists(CURRENT_DIR + '/media'):
        pass
    else:
        os.makedirs(CURRENT_DIR + '/media')

    if os.path.exists(CURRENT_DIR + '/custom_settings.py'):
        sys.path.append(CURRENT_DIR)
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'custom_settings')
    else:
        shutil.copyfile(BASE_DIR + '/custom_settings_tmp.py',
                        CURRENT_DIR + '/custom_settings.py')
        sys.path.append(CURRENT_DIR)
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'custom_settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
