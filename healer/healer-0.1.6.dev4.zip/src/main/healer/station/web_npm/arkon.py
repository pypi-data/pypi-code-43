"""
Provide npm resources
"""

from __future__ import annotations

from healer.station.server.support.arkon import PackageResourceExt


class WebPack(PackageResourceExt):
    "load resource from embedded webpack"

    def __init__(self,
            # identity
            base_path:str,
        ):
        super().__init__(base_path=base_path, import_name=__name__)

    def static_folder(self) -> str:
        return f"target"


class WebResource(PackageResourceExt):
    "load resource from embedded npm package"

    def __init__(self,
            # identity
            base_path:str,
            # npm package
            package_name:str,
        ):
        super().__init__(base_path=base_path, import_name=__name__)
        self.package_name = package_name

    def static_folder(self) -> str:
        return f"node_modules/{self.package_name}"


class WebResourceDist(PackageResourceExt):
    "load resource from embedded npm package"

    def __init__(self,
            # identity
            base_path:str,
            # npm package
            package_name:str,
        ):
        super().__init__(base_path=base_path, import_name=__name__)
        self.package_name = package_name

    def static_folder(self) -> str:
        return f"node_modules/{self.package_name}/dist"
