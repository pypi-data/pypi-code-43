# -*- coding: UTF-8 -*-
from {{app_settings_module}} import *
from lino_local.settings import *

import logging
logging.getLogger('weasyprint').setLevel("ERROR") # see #1462


class Site(Site):
    title = "{{prjname}}"
    server_url = "{{server_url}}"
    {% if webdav %}
    webdav_protocol = 'wdav'
    {% endif %}
    {% if languages %}
    languages = '{{languages}}'
    {% endif %}
    use_linod = {{linod}}
    default_ui = '{{front_end}}'

    def get_plugin_configs(self):
        yield super(Site, self).get_plugin_configs()
        # example of local plugin settings:
        # yield ('ledger', 'start_year', 2018)

SITE = Site(globals())

{% if server_domain == "localhost" %}
DEBUG = True
{% else %}
DEBUG = False
{% endif %}

SECRET_KEY = '{{secret_key}}'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.{{db_engine}}',
        'NAME': '{{db_name}}',
        'USER': '{{db_user}}',
        'PASSWORD': '{{db_password}}',
        'HOST': '{{db_host}}',
        'PORT': {{db_port}},
        {%- if db_engine == "mysql" %}
        'OPTIONS': {
           "init_command": "SET default_storage_engine=MyISAM",
        }
        {% endif -%}
    }
}

EMAIL_SUBJECT_PREFIX = '[{{prjname}}] '

ALLOWED_HOSTS = ['{{server_domain}}']
