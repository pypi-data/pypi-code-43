# Imports from python.
import os


# Imports from Django.
from django.conf import settings as project_settings
from django.test.client import RequestFactory
from django.utils.text import slugify


# Imports from other dependencies.
from rest_framework.renderers import JSONRenderer


# Imports from race_ratings.
from raceratings.exceptions import StaticFileNotFoundError
from raceratings.utils.aws import defaults
from raceratings.utils.aws import get_bucket


class StaticsPublishingMixin(object):
    """
    Handles publishing templates, serialized context and JS/CSS bundles to S3.

    Bundles are published to a directory at paths with this pattern:
    election-results/cdn/{view_name}/{election_date}/{bundle_file}
    """

    def get_request(self, production=False, subpath=""):
        """Construct a request we can use to render the view.

        Send environment variable in querystring to determine whether
        we're using development static file URLs or production."""
        if production:
            env = {"env": "prod"}
        else:
            env = {"env": "dev"}
        kwargs = {**{"subpath": subpath}, **env}
        return RequestFactory().get("", kwargs)

    def get_serialized_context(self):
        """OVERWRITE this method to return serialized context data.

        Use the serializer for the page you would hit.

        Used to bake out serialized context data.
        """
        return {}

    @staticmethod
    def render_static_string(path):
        """Renders static file to string.

        Must have run collectstatic first.
        """
        absolute_path = os.path.join(project_settings.STATIC_ROOT, path)
        try:
            with open(absolute_path, "rb") as staticfile:
                return staticfile.read()
        except (OSError, IOError):
            raise StaticFileNotFoundError(
                "Couldn't find the file {}. Are you sure you configured "
                "static paths correctly on the view and/or have run "
                "collectstatic?".format(path)
            )

    def get_cdn_directory(self):
        """Get slugified view name to use as part of CDN path."""
        return slugify(self.__class__.__name__)

    def get_absolute_js_url(self):
        """Get absolute path to published JS bundle.

        subpath handles primaries, primary runoffs and general runoffs.
        """
        return os.path.join(
            "election-results/cdn/raceratings/",
            "{}/{}".format(self.get_cdn_directory(), self.js_prod_path),
        )

    def get_absolute_css_url(self):
        """Get absolute path to published CSS bundle."""
        return os.path.join(
            "election-results/cdn/raceratings/",
            "{}/{}".format(self.get_cdn_directory(), self.css_prod_path),
        )

    def publish_js(self):
        """Publishes JS bundle."""
        js_string = self.render_static_string(self.js_dev_path)  # noqa
        key = self.get_absolute_js_url()
        print(">>> Publish JS to: ", key)
        bucket = get_bucket()
        bucket.put_object(
            Key=key,
            ACL=defaults.ACL,
            Body=js_string,
            CacheControl=defaults.CACHE_HEADER,
            ContentType="application/javascript",
        )

    def publish_css(self):
        """Publishes CSS bundle."""
        css_string = self.render_static_string(self.css_dev_path)  # noqa
        key = self.get_absolute_css_url()
        print(">>> Publish CSS to: ", key)
        bucket = get_bucket()
        bucket.put_object(
            Key=key,
            ACL=defaults.ACL,
            Body=css_string,
            CacheControl=defaults.CACHE_HEADER,
            ContentType="text/css",
        )

    def publish_serialized_data(self, subpath=""):
        """Publishes serialized data."""
        data = self.get_serialized_data()
        json_string = JSONRenderer().render(data)  # noqa
        key = os.path.join(
            self.get_publish_path(), os.path.join(subpath, "data.json")
        )
        print(">>> Publish data to: ", key)
        bucket = get_bucket()
        bucket.put_object(
            Key=key,
            ACL=defaults.ACL,
            Body=json_string,
            CacheControl=defaults.CACHE_HEADER,
            ContentType="application/json",
        )

    def publish_statics(self, subpath=""):
        self.publish_css()
        self.publish_js()

    def publish_template(self, subpath="", **kwargs):
        """Mocks a request and renders the production template.

        kwargs should be a dictionary of the captured URL values.
        """
        request = self.get_request(production=True, subpath=subpath)
        template_string = self.__class__.as_view()(
            request, **kwargs
        ).rendered_content
        key = os.path.join(
            self.get_publish_path(), os.path.join(subpath, "index.html")
        )
        # TODO: Publish to AWS
        print(">>> Publish template to ", key)
        bucket = get_bucket()
        bucket.put_object(
            Key=key,
            ACL=defaults.ACL,
            Body=template_string,
            CacheControl=defaults.CACHE_HEADER,
            ContentType="text/html",
        )
