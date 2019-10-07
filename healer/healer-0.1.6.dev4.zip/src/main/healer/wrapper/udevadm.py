
from __future__ import annotations

from healer.support.process import ExecuteResult
from healer.wrapper.base import Base
from healer.wrapper.sudo import Sudo


class UdevAdm(Base):

    base = Sudo()

    def __init__(self):
        super().__init__('wrapper/udevadm')

    def rules_reload(self) -> ExecuteResult:
        return self.execute_unit_sert(['control', '--reload-rules'])

    def events_trigger(self) -> ExecuteResult:
        return self.execute_unit_sert(['trigger'])


UDEVADM = UdevAdm()
