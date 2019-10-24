"""TaskBase"""
import json
import logging
import uuid
from typing import Dict, Any, List


class TaskBase:
    transaction_idx_size: int = 1000
    transaction_idx: List[str] = []

    @classmethod
    def pre_fill_transaction_idx(cls) -> None:
        size = cls.transaction_idx_size - len(cls.transaction_idx)
        for _ in range(size):
            cls.transaction_idx.append(' ' * 36)  # uuid4 str size

    @classmethod
    def transaction_id_exists(cls, t_id: str) -> bool:
        if t_id in cls.transaction_idx:
            return True
        else:
            cls.transaction_idx.append(t_id)
            cls.transaction_idx = cls.transaction_idx[1:]
            return False

    def __init__(self, payload: Dict[str, Any], conf: Dict[str, Any]):
        self.t_id: str = payload['transaction_id']
        self.payload: Dict[str, Any] = payload
        self.conf: Dict[str, Any] = conf

    def run_task(self) -> bool:
        if not self.transaction_id_exists(self.t_id):
            return self.task()
        else:
            logging.info('{klass} - This message is a replica - {t_id}'.format(
                klass=self.__class__.__name__.upper(),
                t_id=self.t_id
            ))
            return False

    def task(self) -> bool:
        raise NotImplementedError
