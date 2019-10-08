'''
Compatibility layer for PySide2 quirks...
'''
import qtpy


if qtpy.API_NAME == 'PySide2':
    def Property(cls):
        # Use a basic Python property for PySide2, as the setter does not
        # appear to work in PySide2 5.13.1
        return property
else:
    Property = qtpy.QtCore.Property
