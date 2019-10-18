"""JavascriptMiddleware."""

import os

from jinja2 import Markup

from masonite.request import Request
from masonite.view import View

from .Javascript import Javascript


def get_javascript():
    return Markup(Javascript.render())


class JavascriptMiddleware:
    """Middleware to pass rendered Javascript to the view."""

    def __init__(self, request: Request, view: View):
        """Initialize the JavascriptMiddleware

        Arguments:
            request {masonite.request.Request} -- The normal Masonite request class.
            view {masonite.view.View} -- The normal Masonite view class.
        """
        self.request = request
        self.view = view

    def before(self):
        """Execute this method before the controller."""
        template_var = os.getenv('JS_TEMPLATE_VAR', 'javascript_data')
        self.view.share({ template_var: get_javascript })

    def after(self):
        pass
