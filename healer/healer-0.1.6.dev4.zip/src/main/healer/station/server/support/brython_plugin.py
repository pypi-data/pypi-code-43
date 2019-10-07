"""
Expose brython in flask
"""

from __future__ import annotations

from .arkon import PackageResourceExt


class BrythonRuntimeExt(PackageResourceExt):
    """
    Expose brython javascript runtime in flask
    """

    def __init__(self,
            # blueprint identity, url location
            base_path='brython',
            # resource package provided by 'pip install brython'
            import_name='data',
        ):
        super().__init__(base_path, import_name)
