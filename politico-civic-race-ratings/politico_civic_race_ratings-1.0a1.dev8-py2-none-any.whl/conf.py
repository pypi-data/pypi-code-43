"""
Use this file to configure pluggable app settings and resolve defaults
with any overrides set in project settings.
"""

# Imports from Django.
from django.conf import settings as project_settings


class Settings:
    pass


Settings.SCRATCH_FILE_DIR = getattr(
    project_settings,
    "RACERATINGS_SCRATCH_FILE_DIR",
    getattr(project_settings, "PROJECT_ROOT", ""),
)


settings = Settings
