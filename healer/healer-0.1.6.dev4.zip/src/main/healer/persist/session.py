"""
Sensor record stream persistence
"""

from __future__ import annotations

import atexit
import enum
import os
import re
import shutil
import uuid
from dataclasses import dataclass
from dataclasses import field
from datetime import timezone
from types import FunctionType
from typing import Any
from typing import Type

from healer.config import CONFIG
from healer.persist.support.base import StoredCodec
from healer.persist.support.base import StoredCodecString
from healer.persist.support.mapping import StoredMapping
from healer.support.files import FilesSupport
from healer.support.hronos import DateTime
from healer.support.typing import AutoNameEnum


class SessionType(AutoNameEnum):
    """
    Session storage location type
    """
    cluster = enum.auto()
    private = enum.auto()
    tempdir = enum.auto()


@dataclass(frozen=True)
class SessionIdentity:
    """
    Session naming and location policy
    :instant: session production time, utc
    :trailer: session unique guarantee, guid
    """

    instant:DateTime = field(default_factory=DateTime.utcnow)
    trailer:uuid = field(default_factory=uuid.uuid4)

    @property
    def date_path(self) -> str:
        "produce date based path: YYYY/MM/DD"
        return self.instant.strftime(SessionSupport.format_date_path)

    @property
    def prefix(self) -> str:
        "produce date/time based name prefix: YYYYMMDDTHHMMSS"
        return self.instant.strftime(SessionSupport.format_date_time)

    @property
    def suffix(self) -> str:
        "produce guid based name suffix, to ensure unique session identity"
        return self.trailer.hex

    @property
    def identity(self) -> str:
        "session name policy"
        return f"{self.prefix}-{self.suffix}"

    @property
    def file_name(self) -> str:
        "session file name policy"
        return f"{self.identity}.db"

    @property
    def relative_path(self) -> str:
        "session relative location policy"
        return f"{self.date_path}/{self.file_name}"

    def absolute_path(self, storage_dir:str) -> str:
        "session aboslute location policy"
        return f"{storage_dir}/{self.relative_path}"


@dataclass(init=False)
class PersistSession:
    """
    Persisted device session: sensor message store
    :context_dict: session descriptor / meta data
    :message_dict: collected sensor message stream
    """

    table_context = "context"
    table_message = "message"

    storage_dir:str
    session_identity:SessionIdentity
    codec_class:Type[StoredCodec]

    context_dict:StoredMapping = field(repr=False)
    message_dict:StoredMapping = field(repr=False)

    def __init__(self,
            storage_dir:str,
            session_identity:SessionIdentity=None,
            codec_class:Type[StoredCodec]=None,
        ):
        self.storage_dir = storage_dir
        self.session_identity = session_identity or SessionIdentity()
        self.codec_class = codec_class or StoredCodecString
        self.setup()
        self.touch()

    @property
    def storage_file(self) -> str:
        return self.session_identity.absolute_path(self.storage_dir)

    def setup(self) -> None:
        "ensure settings"
        FilesSupport.ensure_parent(self.storage_file)
        self.context_dict = StoredMapping(
            store_path=self.storage_file, table_name=self.table_context, codec_class=self.codec_class,
        )
        self.message_dict = StoredMapping(
            store_path=self.storage_file, table_name=self.table_message, codec_class=self.codec_class,
        )

    def touch(self):
        "ensure disk file"
        self.context_dict.touch()
        self.message_dict.touch()

    def move_to(self, storage_dir:str) -> None:
        "relocate session store to a new location"
        self.touch()
        source_path = self.storage_file  # past
        self.storage_dir = storage_dir
        target_path = self.storage_file  # next
        FilesSupport.ensure_parent(target_path)
        shutil.move(source_path, target_path)
        self.setup()
        self.touch()

    def open(self) -> None:
        self.context_dict.open()
        self.message_dict.open()

    def close(self) -> None:
        self.context_dict.close()
        self.message_dict.close()

    def context_get(self, key:str, default:Any=None) -> Any:
        return self.context_dict.get(key, default)

    def context_put(self, key:str, value:Any) -> None:
        self.context_dict[key] = value

    def message_get(self, key:str, default:Any=None) -> Any:
        return self.message_dict.get(key, default)

    def message_put(self, key:str, value:Any) -> None:
        self.message_dict[key] = value

    def __enter__(self) -> None:
        self.open()

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.close()


class SessionSupport:
    """
    persisted session lifesize
    """

    # session identity prefix
    format_date_time = '%Y%m%dT%H%M%S'

    # session location folder
    format_date_path = '%Y/%m/%d'

    # extract identity segments
    regex_session_file = re.compile(
        "^([0-9]{4})([0-9]{2})([0-9]{2})T([0-9]{2})([0-9]{2})([0-9]{2})-([0-9a-z]{32})[.]db$",
        re.RegexFlag.IGNORECASE,
    )

    @staticmethod
    def extract_identity(session_path:str) -> SessionIdentity:
        "parse session file path to produce session identity object"
        session_file = os.path.basename(session_path)
        session_match = SessionSupport.regex_session_file.match(session_file)
        assert session_match, f"wrong session_path: {session_path}"
        instant = DateTime(
            year=int(session_match.group(1)),
            month=int(session_match.group(2)),
            day=int(session_match.group(3)),
            hour=int(session_match.group(4)),
            minute=int(session_match.group(5)),
            second=int(session_match.group(6)),
            tzinfo=timezone.utc,
        )
        trailer = uuid.UUID(session_match.group(7))
        return SessionIdentity(instant=instant, trailer=trailer,)

    @staticmethod
    def session_folder(session_type:SessionType) -> str:
        "find session folder by session type"
        section = CONFIG['storage']
        if session_type == SessionType.cluster:
            return section['cluster_session']
        elif session_type == SessionType.private:
            return section['private_session']
        elif session_type == SessionType.tempdir:
            return section['tempdir_session']
        else:
            raise RuntimeError(f"wrong session: {session_type}")

    @staticmethod
    def destroy_session(session:PersistSession) -> None:
        session.close()
        FilesSupport.desure_path(session.storage_file)

    @staticmethod
    def produce_session(
            session_identity:SessionIdentity=None,
            session_type:SessionType=None,
            codec_class:Type[StoredCodec]=None,
        ) -> PersistSession:
        "persisted session factory"
        session_type = session_type or SessionType.tempdir
        session_identity = session_identity or SessionIdentity()
        codec_class = codec_class or StoredCodecString
        storage_dir = SessionSupport.session_folder(session_type)
        storage_path = session_identity.absolute_path(storage_dir)
        if session_type == SessionType.tempdir:
            atexit.register(FilesSupport.desure_path, storage_path)
        session = PersistSession(
            storage_dir=storage_dir, session_identity=session_identity, codec_class=codec_class,
        )
        session.open()
        return session

    @staticmethod
    def move_to_type(session:PersistSession, session_type:SessionType) -> None:
        storage_dir = SessionSupport.session_folder(session_type)
        session.move_to(storage_dir)

    @staticmethod
    def move_to_cluster(session:PersistSession) -> None:
        SessionSupport.move_to_type(session, SessionType.cluster)

    @staticmethod
    def move_to_private(session:PersistSession) -> None:
        SessionSupport.move_to_type(session, SessionType.private)

    @staticmethod
    def session_visit(session_type:SessionType, visitor_function:FunctionType) -> None:
        "apply visitor function to sessions present in the store"
        storage_dir = SessionSupport.session_folder(session_type)
        SessionSupport.session_visit_dir(storage_dir, visitor_function)

    @staticmethod
    def session_visit_dir(storage_dir:str, visitor_function:FunctionType) -> None:
        "apply visitor function to sessions present in the store, with sorted ordering"
        for base_path, dir_name_list, file_name_list in os.walk(storage_dir):
            dir_name_list.sort()  # string sort
            file_name_list.sort()  # string sort
            for file_name in file_name_list:
                file_path = os.path.join(base_path, file_name)
                visitor_function(file_path)
