import json
import zipfile
from datetime import datetime
from hashlib import sha1
from io import BytesIO
from itertools import tee, filterfalse
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Tuple

import click
import pytz
import requests

from ignot.models import *

RespInfo = Tuple[int, str]
FileNames = Tuple[str, str]


def get_vanilla_manifest() -> VanillaManifest:
    path = Path(__file__).parent / "data" / "vanilla.json"
    manifest = VanillaManifest.parse_file(path)
    click.echo(
        click.style(f"Loaded vanilla manifest: ", fg="green") +
        click.style(manifest.id, bold=True)
    )
    return manifest


def get_mc4ep_authlib() -> VanillaLibrary:
    path = Path(__file__).parent / "data" / "authlib.json"
    library = VanillaLibrary.parse_file(path)
    click.echo(
        click.style(f"Loaded authlib from MC4EP: ", fg="green") +
        click.style(library.name, bold=True)
    )
    return library


def get_liteloader_library() -> VanillaLibrary:
    path = Path(__file__).parent / "data" / "liteloader.json"
    library = VanillaLibrary.parse_file(path)
    click.echo(
        click.style(f"Loaded LiteLoader library: ", fg="green") +
        click.style(library.name, bold=True)
    )
    return library


def tweak_liteloader_arg(source: str) -> str:
    tweak = "--tweakClass com.mumfrey.liteloader.launch.LiteLoaderTweaker"
    return f"{tweak} {source}"


def extract_forge_manifest(installer_blob: bytes) -> ForgeManifest:
    profile_name = "install_profile.json"
    with TemporaryDirectory() as dest, zipfile.ZipFile(BytesIO(installer_blob), 'r') as zip_ref:
        zip_ref.extract(profile_name, dest)
        data = json.load((Path(dest) / profile_name).open())
        click.echo(
            click.style(f"Extracted clean forge profile: ", fg="green") +
            click.style(data['install']['path'], bold=True)
        )
        return InstallProfile(**data).versionInfo


def download_forge_installer(version: str) -> bytes:
    path = (
        "https://files.minecraftforge.net/"
        "maven/net/minecraftforge/forge/"
        f"1.12.2-{version}/"
        f"forge-1.12.2-{version}-installer.jar"
    )
    click.echo(
        click.style(f"Downloading Forge installer from: ", fg="green") +
        click.style(path, bold=True)
    )
    return requests.get(path).content


def save_manifest(version_storage: Path, name: str, manifest: GameManifest):
    bundle_dir = version_storage / name
    bundle_dir.mkdir(parents=True)
    manifest_file = bundle_dir / f"{name}.json"
    with manifest_file.open('w') as file_handler:
        json.dump(manifest.dict(), file_handler, ensure_ascii=False, indent=2)
    click.echo(
        click.style("Successfully stored game manifest: ", fg="green") +
        click.style(manifest_file.as_posix(), bold=True)
    )


def download_client(version_storage: Path, name: str, manifest: GameManifest):
    client_path = version_storage / name / f"{name}.jar"
    data = requests.get(manifest.downloads.client.url).content
    client_path.write_bytes(data)
    click.echo(
        click.style(f"Successfully downloaded vanilla client from ", fg="green") +
        click.style(manifest.downloads.client.url, bold=True)
    )


def _partition(pred, iterable):
    t1, t2 = tee(iterable)
    return list(filterfalse(pred, t1)), list(filter(pred, t2))


def _predicate_native(library: VanillaLibrary) -> bool:
    return library.natives is None


def _integrity_check(
    url: str,
    stored_size: int,
    stored_digest: str,
    downloaded_size: int,
    downloaded_digest: str
) -> bool:
    broken = downloaded_size != stored_size or downloaded_digest != stored_digest
    if broken:
        click.echo(click.style(
            f"Content for {url} has broken but size and/or hash.\n"
            f"Need: {stored_size} bytes, got {downloaded_size} bytes; "
            f"Need: {stored_digest} digest, got {downloaded_digest} digest"
            f"This is an error!", fg="red"
        ))
    return not broken


def _store_blob(source: Union[Download, str], destination: Path) -> RespInfo:
    if isinstance(source, Download):
        if destination.exists():
            stored = destination.read_bytes()
            stored_digest = sha1(stored).hexdigest()
            source_digest = source.sha1
            if stored_digest != source_digest:
                click.echo(click.style(
                    f"Stored library for {source.url} in {destination.as_posix()} is outdated or broken.\n"
                    f"Need: {source_digest} digest, got {stored_digest} digest"
                    f"This is an error!", fg="red"
                ))
                raise IOError("Hash mismatch!")
            click.echo(click.style(f"File {destination.as_posix()} already exists, skipping it.", dim=True))
        else:
            response = requests.get(source.url)
            status = response.status_code
            if status != 200:
                click.echo(click.style(f"Failed to download {source.url}, response: {status}", fg="red"))
                raise IOError("Broken library!")

            downloaded: bytes = response.content
            downloaded_digest = sha1(downloaded).hexdigest()
            source_digest = source.sha1
            if downloaded_digest != source_digest:
                click.echo(click.style(
                    f"Downloaded broken library from {source.url}.\n"
                    f"Need: {source_digest} digest, got {downloaded_digest} digest"
                    f"This is an error!", fg="red"
                ))
                raise IOError("Hash mismatch!")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(downloaded)
        return source.size, source.sha1
    else:
        response = requests.get(source)
        status = response.status_code
        if status != 200:
            click.echo(click.style(f"Failed to download {source}, response: {status}", fg="red"))
            raise IOError("Broken library!")
        downloaded: bytes = response.content
        downloaded_digest = sha1(downloaded).hexdigest()
        downloaded_length = len(downloaded)

        if destination.exists():
            stored = destination.read_bytes()
            stored_digest = sha1(stored).hexdigest()
            if downloaded_digest != stored_digest:
                click.echo(click.style(
                    f"Downloaded broken library from {source}.\n"
                    f"Need: {stored_digest} digest, got {downloaded_digest} digest"
                    f"This is an error!", fg="red"
                ))
                raise IOError("Hash mismatch!")
            click.echo(click.style(f"File {destination.as_posix()} already exists, skipping it.", dim=True))
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(downloaded)
        return downloaded_length, downloaded_digest


def _patch_forge_locations(groups_chunk: str, name: str, version: str) -> FileNames:
    local_artifact_name = f"{name}-{version}.jar"
    if groups_chunk == "net.minecraftforge" and name == "forge":
        return local_artifact_name, f"{name}-{version}-universal.jar"  # Shitty Forge…
    return local_artifact_name, local_artifact_name


def infer_location(maven_coordinates: str) -> Tuple[Path, Path]:
    """
    See https://cwiki.apache.org/confluence/display/MAVENOLD/Repository+Layout+-+Final
    """
    groups_chunk, name, version, *_ = maven_coordinates.split(":")  # Ignore classifiers by now
    groups = groups_chunk.split(".")
    local_filename, remote_filename = _patch_forge_locations(groups_chunk, name, version)
    return Path(*groups, name, version, local_filename), Path(*groups, name, version, remote_filename)


def _download_vanilla_library(library: VanillaLibrary, storage: Path) -> VanillaLibrary:
    path, _ = infer_location(library.name)
    if library.downloads.artifact is not None:
        destination = storage / path
        _store_blob(library.downloads.artifact, destination)
    if library.downloads.classifiers is not None:
        for classifier, artifact in library.downloads.classifiers.items():
            destination = storage / path.parent / f"{path.stem}-{classifier}{path.suffix}"
            _store_blob(artifact, destination)
    return library


def infer_repository(library: ForgeLibrary) -> str:
    groups_chunk, *_ = library.name.split(":")

    if groups_chunk in {"net.minecraftforge", "org.scala-lang"}:
        return "http://files.minecraftforge.net/maven"
    if groups_chunk in {"net.minecraft", "lzma", "java3d"}:
        return "https://libraries.minecraft.net"
    return "https://repo1.maven.org/maven2"


def _download_forge_library(library: ForgeLibrary, storage: Path) -> VanillaLibrary:
    local_path, remote_path = infer_location(library.name)
    base_url = infer_repository(library)
    url = f"{base_url}/{remote_path.as_posix()}"
    destination = storage / local_path
    size, digest = _store_blob(url, destination)
    return VanillaLibrary(
        name=library.name,
        downloads=VanillaDownload(artifact=Download(url=url, sha1=digest, size=size))
    )


def download_vanilla_libraries(libraries: List[VanillaLibrary], storage: Path) -> List[VanillaLibrary]:
    platform, common = _partition(_predicate_native, libraries)
    click.echo(click.style(
        f"Going to process {len(common)} common and {len(platform)} "
        f"platform-dependent libraries", fg="green"
    ))
    return [_download_vanilla_library(l, storage) for l in libraries]


def download_forge_libraries(libraries: List[ForgeLibrary], storage: Path) -> List[VanillaLibrary]:
    click.echo(f"Going to process {len(libraries)} Forge libraries")
    return [_download_forge_library(l, storage) for l in libraries]


def replace_authlib(libraries: List[VanillaLibrary]) -> List[VanillaLibrary]:
    authlib = get_mc4ep_authlib()
    filtered = [l for l in libraries if "authlib" not in l.name]
    click.echo(
        click.style(f"Replaced authlib with MC4EP variant: ", fg="green") +
        click.style(authlib.name, bold=True)
    )
    return sorted([authlib, *filtered])


def add_liteloader_lib(libraries: List[VanillaLibrary]) -> List[VanillaLibrary]:
    ll_lib = get_liteloader_library()
    click.echo(
        click.style(f"Added LiteLoader library: ", fg="green") +
        click.style(ll_lib.name, bold=True)
    )
    return sorted([ll_lib, *libraries])


def merge_manifests(
    name: str,
    vanilla: VanillaManifest,
    forge: ForgeManifest,
    libraries: List[VanillaLibrary],
    with_liteloader: bool
) -> GameManifest:
    args = with_liteloader and tweak_liteloader_arg(forge.minecraftArguments) or forge.minecraftArguments

    return GameManifest(
        id=name,
        checksum=vanilla.downloads.client.sha1,
        time=datetime.now(pytz.utc).strftime("%Y-%m-%dT%H:%M:%S%z"),
        releaseTime="1960-01-01T00:00:00-0700",
        type="release",
        minecraftArguments=args,
        libraries=libraries,
        mainClass=forge.mainClass,
        jar=forge.jar,
        minimumLauncherVersion=vanilla.minimumLauncherVersion,
        assets=vanilla.assets,
        downloads=vanilla.downloads,
        assetIndex=vanilla.assetIndex,
        logging=forge.logging,
    )
