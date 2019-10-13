import os
from copy import deepcopy
from pathlib import Path

import click

from ignot import bundle


@click.command()
@click.option("--name", required=True, type=str, help="Manifest name (internal identifier)")
@click.option("--forge-version", type=str, default="14.23.5.2768", help="Forge version", show_default=True)
@click.option('--with-liteloader', is_flag=True, default=True, help="Whether to add LiteLoader?", show_default=True)
@click.option('--auth-type', type=click.Choice(['vanilla', 'mc4ep']), default="mc4ep", help="Authentication system", show_default=True)
def cli(name: str, forge_version: str, with_liteloader: bool, auth_type: str):
    """Create new version manifest"""
    storage_path = Path(os.environ.get("IGNOT_STORAGE", os.getcwd()))
    click.echo(
        click.style(f"Base storage: ", fg="blue") +
        click.style(storage_path.as_posix(), bold=True)
    )
    library_storage = storage_path / "libraries"
    version_storage = storage_path / "versions"
    with_mc4ep_authlib = auth_type == "mc4ep"

    vanilla = bundle.get_vanilla_manifest()
    installer_blob = bundle.download_forge_installer(forge_version)
    forge = bundle.extract_forge_manifest(installer_blob)

    if with_mc4ep_authlib:
        vanilla_libraries = bundle.replace_authlib(deepcopy(vanilla.libraries))
    else:
        vanilla_libraries = vanilla.libraries

    if with_liteloader:
        vanilla_libraries = bundle.add_liteloader_lib(vanilla_libraries)

    libraries = [
        *bundle.download_vanilla_libraries(vanilla_libraries, library_storage),
        *bundle.download_forge_libraries(forge.libraries, library_storage)
    ]

    game_manifest = bundle.merge_manifests(
        name,
        vanilla,
        forge,
        libraries,
        with_liteloader
    )

    bundle.save_manifest(version_storage, name, game_manifest)
    bundle.download_client(version_storage, name, game_manifest)


if __name__ == '__main__':
    cli()
