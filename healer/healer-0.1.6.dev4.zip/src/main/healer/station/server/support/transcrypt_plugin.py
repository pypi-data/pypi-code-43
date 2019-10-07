"""
Expose transcrypt in flask
"""

from __future__ import annotations

from .arkon import PackageResourceExt


class TranscryptResourceExt(PackageResourceExt):
    """
    Expose transcrypt javascript resources in flask
    """

    def __init__(self,
            # blueprint identity, url location
            base_path,
            # resource package'
            import_name,
            # transcrypt compiler output
            static_path="__target__",

        ):
        super().__init__(base_path, import_name, static_path)
