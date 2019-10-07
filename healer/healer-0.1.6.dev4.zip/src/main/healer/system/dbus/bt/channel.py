"""
Bluetooth connection channels
"""

from __future__ import annotations

import abc
import os

from gi.repository import GObject

from healer.support.typing import unused


class WithBluetoothSerialChannel(abc.ABC):
    """
    Trait: bluetooth serial profile connection via file descriptor
    """

    # channel file descriptor
    serial_file_desc:int

    # channel selector descriptor
    serial_select_id:int

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serial_file_desc = -1
        self.serial_select_id = -1

    @abc.abstractmethod
    def serial_react_read(self, buffer:bytes) -> None:
        "process received bytes buffer"

    def serial_issue_read(self, file_desc:int, cond_mask:int) -> bool:
        unused(cond_mask)
        size = 1024  # TODO config
        buffer = os.read(file_desc, size)
        assert len(buffer) > 0 and len(buffer) < size
        self.serial_react_read(buffer)
        return True

    def serial_issue_write(self, buffer:bytes) -> None:
        assert self.serial_file_desc > 0
        size = os.write(self.serial_file_desc, buffer)
        assert size == len(buffer)

    def serial_channel_connect(self, file_desc:int) -> None:
        assert file_desc > 0
        assert self.serial_file_desc < 0
        self.serial_file_desc = file_desc
        self.serial_select_id = GObject.io_add_watch(
            self.serial_file_desc,
            GObject.IO_IN,
            self.serial_issue_read,
        )

    def serial_channel_disconnect(self) -> None:
        if self.serial_file_desc > 0:
            os.close(self.serial_file_desc)
            self.serial_file_desc = -1
            GObject.source_remove(self.serial_select_id)
            self.serial_select_id = -1
