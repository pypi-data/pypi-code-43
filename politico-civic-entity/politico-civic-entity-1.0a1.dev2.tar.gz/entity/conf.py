"""
Use this file to configure pluggable app settings and resolve defaults
with any overrides set in project settings.
"""

# Imports from Django.
from django.conf import settings as project_settings


class Settings:
    pass


Settings.AWS_ACCESS_KEY_ID = getattr(
    project_settings, "ENTITY_AWS_ACCESS_KEY_ID", None
)

Settings.AWS_SECRET_ACCESS_KEY = getattr(
    project_settings, "ENTITY_AWS_SECRET_ACCESS_KEY", None
)

Settings.AWS_S3_BUCKET = getattr(
    project_settings, "ENTITY_AWS_S3_BUCKET", None
)

Settings.CLOUDFRONT_ALTERNATE_DOMAIN = getattr(
    project_settings, "ENTITY_CLOUDFRONT_ALTERNATE_DOMAIN", None
)

Settings.S3_UPLOAD_ROOT = getattr(
    project_settings, "ENTITY_S3_UPLOAD_ROOT", "uploads/entity"
)

Settings.AWS_S3_ACL = getattr(
    project_settings, "ENTITY_AWS_S3_ACL", "public-read"
)

Settings.API_AUTHENTICATION_CLASS = getattr(
    project_settings,
    "ENTITY_API_AUTHENTICATION_CLASS",
    "rest_framework.authentication.BasicAuthentication",
)

Settings.API_PERMISSION_CLASS = getattr(
    project_settings,
    "ENTITY_API_PERMISSION_CLASS",
    "rest_framework.permissions.IsAdminUser",
)

Settings.API_PAGINATION_CLASS = getattr(
    project_settings,
    "ENTITY_API_PAGINATION_CLASS",
    "entity.pagination.ResultsPagination",
)

settings = Settings
