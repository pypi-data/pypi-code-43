from enum import Enum
from typing import Optional, Dict, List, Union

from pydantic import BaseModel


class Download(BaseModel):
    url: str
    sha1: str
    size: int

    class Config:
        allow_mutation = False

    def __hash__(self):
        return hash((self.url, self.sha1, self.size))

    def __eq__(self, other):
        return hash(self) == hash(other)


class Artifact(BaseModel):
    url: Optional[str] = None
    sha1: str
    size: int
    path: str

    class Config:
        allow_mutation = False

    def __hash__(self):
        return hash((self.path,))

    def __eq__(self, other):
        return hash(self) == hash(other)


class VanillaExtract(BaseModel):
    exclude: List[str]

    class Config:
        allow_mutation = False

    def __hash__(self):
        return hash(frozenset(self.exclude))

    def __eq__(self, other):
        return hash(self) == hash(other)


class VanillaDownload(BaseModel):
    artifact: Optional[Download] = None
    classifiers: Optional[Dict[str, Download]] = None

    class Config:
        allow_mutation = False

    def __hash__(self):
        return hash((
            self.artifact,
            self.classifiers and frozenset(self.classifiers.values()) or self.classifiers,
        ))

    def __eq__(self, other):
        return hash(self) == hash(other)


class VanillaAction(str, Enum):
    ALLOW = 'allow'
    DISALLOW = 'disallow'


class VanillaOS(BaseModel):
    name: str

    class Config:
        allow_mutation = False

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return hash(self) == hash(other)


class VanillaRule(BaseModel):
    action: VanillaAction
    os: Optional[VanillaOS] = None


class VanillaLibrary(BaseModel):
    name: str
    downloads: VanillaDownload
    natives: Optional[Dict[str, str]] = None
    extract: Optional[VanillaExtract] = None
    rules: Optional[List[VanillaRule]] = None

    class Config:
        allow_mutation = False

    def __hash__(self):
        return hash((
            self.name,
            self.downloads,
            self.natives and frozenset(self.natives.values()) or self.natives,
            self.extract,
            self.rules and frozenset(self.rules) or self.rules,
        ))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __lt__(self, other):
        return self.name < other.name


class ForgeLibrary(BaseModel):
    name: str
    url: Optional[str] = None
    artifact: Optional[Artifact] = None
    checksums: Optional[List[str]] = None  # FIXME: drop?
    serverreq: bool = False
    clientreq: bool = True

    class Config:
        allow_mutation = False

    def __hash__(self):
        return hash((
            self.name,
            self.url,
            self.artifact,
            self.checksums and frozenset(self.checksums) or self.checksums,
            self.serverreq,
            self.clientreq
        ))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __lt__(self, other):
        return self.name < other.name


class DownloadManifest(BaseModel):
    client: Download
    server: Download

    class Config:
        allow_mutation = False

    def __hash__(self):
        return hash((self.client, self.server))

    def __eq__(self, other):
        return hash(self) == hash(other)


class AssetIndex(Download):
    id: str
    totalSize: int = 0
    known: bool = True

    class Config:
        allow_mutation = False

    def __hash__(self):
        return hash((self.id, self.totalSize, self.known))

    def __eq__(self, other):
        return hash(self) == hash(other)


class VanillaManifest(BaseModel):
    id: str
    time: str
    releaseTime: str
    type: str
    minecraftArguments: str
    libraries: List[VanillaLibrary]
    mainClass: str
    minimumLauncherVersion: int = 18
    assets: str
    downloads: DownloadManifest
    assetIndex: AssetIndex

    class Config:
        allow_mutation = False

    def __hash__(self):
        return hash((
            self.id,
            self.time,
            self.releaseTime,
            self.type,
            self.minecraftArguments,
            self.mainClass,
            self.minimumLauncherVersion,
            self.assets,
            self.downloads,
            self.assetIndex,
            frozenset(self.libraries),
        ))

    def __eq__(self, other):
        return hash(self) == hash(other)


class ForgeManifest(BaseModel):
    id: str
    time: str
    releaseTime: str
    type: str
    minecraftArguments: str
    libraries: List[ForgeLibrary]
    mainClass: str
    jar: str
    logging: Dict[str, str] = {}

    class Config:
        allow_mutation = False

    def __hash__(self):
        return hash((
            self.id,
            self.time,
            self.releaseTime,
            self.type,
            self.minecraftArguments,
            self.mainClass,
            self.jar,
            frozenset(self.logging.values()),
            frozenset(self.libraries),
        ))

    def __eq__(self, other):
        return hash(self) == hash(other)


class InstallProfile(BaseModel):
    versionInfo: ForgeManifest

    # Ignore rest of fields

    class Config:
        allow_mutation = False


class GameManifest(BaseModel):
    id: str
    checksum: str
    time: str
    releaseTime: str
    type: str
    minecraftArguments: str
    libraries: List[Union[VanillaLibrary, ForgeLibrary]]
    mainClass: str
    jar: str
    minimumLauncherVersion: int = 18
    assets: str
    downloads: DownloadManifest
    assetIndex: AssetIndex
    logging: Dict[str, str] = {}

    class Config:
        allow_mutation = False
