from django.apps import AppConfig as DjangoApponfig


class AppConfig(DjangoApponfig):
    name = "meta_permissions"
    verbose_name = "Meta Authentication and Permissions"
