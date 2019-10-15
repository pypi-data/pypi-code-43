from queue import Queue, Empty


TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


class _queue(Queue):
    """
    Items in a data_view are immutable.
    """
    CREATE = 0
    UPDATE = 1
    DELETE = 2

    def __init__(self, name):
        super().__init__()
        self.name = name
        self._log = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    def __call__(self, qid, start_time, end_time, limit):
        raise NotImplementedError

    def get(self, block=False, timeout=None, forget=False):
        item = super().get(block, timeout)
        if forget:
            self._log.append((self.DELETE, item))
        return item

    def get_all(self, block=False, timeout=None, forget=False):
        try:
            while True:
                yield self.get(block, timeout, forget)
        except Empty:
            return

    def get_to_dataframe(self):
        import pandas as pd
        df = pd.DataFrame(list(self.get_all()))
        if len(df) > 0:
            df['ts'] = pd.to_datetime(df['ts'])
        return df

    def put(self, item, block=False, timeout=None, forget=False):
        super().put(item)
        if not forget:
            self._log.append((self.CREATE, item))

    def put_all(self, items, block=False, timeout=None, forget=False):
        for item in items:
            self.put(item, block, timeout, forget)

    def put_from_dataframe(self, df):
        import pandas as pd
        if len(df) == 0:
            return
        self.put_all([{'qid': d['qid'], 'ts': pd.to_datetime(d['ts']).strftime(TIME_FORMAT), 'val': d['val']}
                      for d in df.to_records()])

    def clear(self, forget=False):
        if forget:
            self.get_all(False, forget=True)
        else:
            with self.mutex:
                self.queue.clear()

    def get_log(self):
        # TODO: collapse this in an intelligent way
        return self._log
