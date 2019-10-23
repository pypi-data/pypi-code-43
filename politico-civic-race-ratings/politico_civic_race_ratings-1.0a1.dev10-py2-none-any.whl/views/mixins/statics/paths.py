# Imports from python.
import os
import uuid


# Imports from Django.
from django.templatetags.static import static


class StaticsPathsMixin(object):
    """
    Handling for static file URLs, which are passed to the template as context.

    Bundles are published to a directory at paths with this pattern:
    election-results/cdn/{view_name}/{election_date}/{bundle_file}
    """

    hash = uuid.uuid4().hex[:10]
    js_dev_path = None
    js_prod_path = "script-{}.js".format(hash)

    css_dev_path = None
    css_prod_path = "styles-{}.css".format(hash)

    def get_static_paths(self, production=False):
        """Returns paths for static files."""
        if production:
            return {
                "js": os.path.join(
                    self.static_path, self.get_absolute_js_url()
                ),
                "css": os.path.join(
                    self.static_path, self.get_absolute_css_url()
                ),
            }
        return {
            "js": static(self.js_dev_path),
            "css": static(self.css_dev_path),
        }

    def get_extra_static_paths(self, production=False):
        """OVERWRITE this method to return paths for extra data resources.

        e.g., { "context": "path/to/context/data.json" }
        """
        if production:
            return {}
        return {}

    def get_paths_context(self, production=False):
        """Build paths to static files and data."""
        return {
            "paths": {
                **self.get_static_paths(production),
                **self.get_extra_static_paths(production),
            }
        }
