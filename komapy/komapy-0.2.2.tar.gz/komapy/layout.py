"""
KomaPy chart layout.
"""

from .exceptions import ChartError
from .utils import get_validation_methods


class Layout(object):
    """A layout object."""

    def __init__(self, **kwargs):
        self.type = kwargs.get('type', 'default')
        self.size = kwargs.get('size', [])
        self.data = kwargs.get('data', [])
        self.options = kwargs.get('options', {})

    def validate_size(self):
        """Validate layout size attribute."""
        if self.type == 'grid':
            if not self.size:
                raise ChartError(
                    "Layout size must be set "
                    "if layout type is 'grid'")

            if len(self.size) != 2:
                raise ChartError('Layout size length must be 2')

    def validate_data(self):
        """Validate layout data attribute."""
        if self.type == 'grid':
            for layout in self.data:
                grid = layout.get('grid')
                if not grid:
                    raise ChartError(
                        "Layout grid setting must be set "
                        "if layout type is 'grid'")

                if not grid.get('location'):
                    raise ChartError(
                        "Layout grid location must be set "
                        "if layout type is 'grid'")

                if len(grid['location']) != 2:
                    raise ChartError("Layout grid location length must be 2")

    def validate(self):
        """Validate all config attributes."""
        validation_methods = get_validation_methods(Layout)

        for method in validation_methods:
            getattr(self, method)()
