from flask import current_app

from .config import streamcomfiguration


def add_apivideo_config(app):
    with app.app_context():
        current_app.config.from_object(streamcomfiguration.configuration['default'])
