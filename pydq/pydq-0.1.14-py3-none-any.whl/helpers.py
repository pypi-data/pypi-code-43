import json
from datetime import datetime
from pydq import TIME_FORMAT


class DqConfig:
    def __init__(self, name, dq_provider, qname='Config', default_config={}):
        self.data_queue = dq_provider(qname)
        self.config_name = name
        self.config = default_config
        self.old_config = None

    def __enter__(self):
        self.data_queue.__enter__()
        self.data_queue(qid=self.config_name, limit=1)      # load from storage
        if self.data_queue.qsize() > 0:
            self.old_config = json.loads(self.data_queue.get()['val'])
            self.config.update(self.old_config)
        return self.config

    def __exit__(self, exc_type, exc_val, exc_tb):
        val = json.dumps(self.config, sort_keys=True)
        old_val = json.dumps(self.old_config, sort_keys=True) if self.old_config is not None else None
        if old_val != val:
            self.data_queue.put({'qid': self.config_name,
                                 'ts': datetime.strftime(datetime.utcnow(), TIME_FORMAT),
                                 'val': val})
        self.data_queue.__exit__(exc_type, exc_val, exc_tb)


def list_all(dq_provider):
    return dq_provider.list_all()
