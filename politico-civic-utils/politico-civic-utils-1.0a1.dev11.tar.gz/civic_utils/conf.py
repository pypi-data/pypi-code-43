"""
Use this file to configure pluggable app settings and resolve defaults
with any overrides set in project settings.
"""

# Imports from Django.
from django.conf import settings as project_settings


class Settings:
    pass


Settings.AWS_ACCESS_KEY_ID = getattr(
    project_settings, "CIVIC_UTILS_AWS_ACCESS_KEY_ID", None
)

Settings.AWS_SECRET_ACCESS_KEY = getattr(
    project_settings, "CIVIC_UTILS_AWS_SECRET_ACCESS_KEY", None
)

Settings.AWS_S3_BUCKET = getattr(
    project_settings, "CIVIC_UTILS_AWS_S3_BUCKET", None
)

Settings.FIXTURE_ROOT_PATH = getattr(
    project_settings, "CIVIC_UTILS_FIXTURE_ROOT", None
)

settings = Settings
