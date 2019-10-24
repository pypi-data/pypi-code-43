"""TaskBase"""
import logging
from typing import Dict, Any, List


class TaskBase:
    TRANSACTION_IDX_SIZE: int = 1000

    def pre_fill_transaction_idx(self) -> None:
        size = self.__class__.TRANSACTION_IDX_SIZE - len(self.transaction_idx)
        for _ in range(size):
            self.transaction_idx.append(' ' * 36)  # uuid4 str size

    def transaction_id_exists(self, t_id: str) -> bool:
        if t_id in self.transaction_idx:
            return True
        elif len(self.transaction_idx) == self.__class__.TRANSACTION_IDX_SIZE:
            self.transaction_idx.append(t_id)
            self.transaction_idx = self.transaction_idx[1:]
            return False
        else:
            self.transaction_idx.append(t_id)
            return False

    def __init__(self, conf: Dict[str, Any], pre_fill: bool=True):
        self.conf: Dict[str, Any] = conf
        self.transaction_idx = []
        if pre_fill:
            self.pre_fill_transaction_idx()

    def run_task(self, payload: Dict[str, Any], t_id: str) -> bool:
        if not self.transaction_id_exists(t_id):
            return self.task(payload)
        else:
            logging.info('{klass} - This message is a replica - {t_id}'.format(
                klass=self.__class__.__name__.upper(),
                t_id=t_id
            ))
            return False

    def task(self, payload: Dict[str, Any]) -> bool:
        raise NotImplementedError
