import sys
import traceback
import aiohttp
import asyncio
import dateutil.parser
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import List, Optional, Callable

from functools import wraps

from acapelladb import Session


class BatchException(Exception):
    pass


class BatchDoesNotExist(BatchException):
    pass


class BatchSendError(BatchException):
    pass


aiohttp_errors = (
    aiohttp.client_exceptions.ClientResponseError,
    aiohttp.client_exceptions.ClientOSError,
    aiohttp.client_exceptions.ServerDisconnectedError,
    aiohttp.client_exceptions.ServerTimeoutError,
    asyncio.TimeoutError
)


def log_aiohttp_error(e, logger):
    try:
        code = e.code
    except AttributeError:
        code = ''

    if logger:
        logger.warn(f'{e.__class__.__name__}: {code}')


def with_retries(partition_key: List[str] = None, clustering_key: Optional[List[str]] = None,
                 backoff: int = 2, retries_max: int = -1, success_max: int = -1, logger: object = None):
    def dec(f):
        @wraps(f)
        async def decorator(*args, **kwargs):
            backoff_timeout = 1
            retry_count = 0
            success_count = 0

            with_retries_logger = logger or kwargs.get('logger')

            res = None

            while True:
                try:
                    res = await f(*args, **kwargs)
                    success_count += 1
                    backoff_timeout = 1
                    if with_retries_logger:
                        with_retries_logger.warn(f'backoff timeout reset, now: {backoff_timeout} sec')
                except TimeoutError:
                    if backoff_timeout > 1:
                        backoff_timeout = 1
                        if with_retries_logger:
                            with_retries_logger.warn(f'backoff timeout reset, now: {backoff_timeout} sec')

                    if with_retries_logger:
                        partition = partition_key if partition_key else kwargs.get('partition_key')
                        clustering = clustering_key if clustering_key else kwargs.get('clustering_key')
                        with_retries_logger.warn(f'partition {partition} | clustering {clustering}: timeout')

                except (*aiohttp_errors,
                        asyncio.TimeoutError) as e:
                    log_aiohttp_error(e, with_retries_logger)
                    retry_count += 1

                    if retry_count == retries_max:
                        if with_retries_logger:
                            with_retries_logger.warn('no more retries, exit')
                        break

                    await asyncio.sleep(backoff_timeout)
                    backoff_timeout *= backoff
                    if with_retries_logger:
                        with_retries_logger.warn(f'backoff timeout increase, now: {backoff_timeout} sec')
                except Exception as e:
                    if with_retries_logger:
                        lines = []
                        for line in traceback.format_exception(*sys.exc_info()):
                            lines.append(line)

                        with_retries_logger.error(e, exc_info=True)
                    break
                else:
                    retry_count = 1

                if success_count == success_max:
                    break

            return res

        return decorator

    return dec


@with_retries(success_max=1)
async def send_batch(batch, logger):
    print("SENDING")
    await batch.send()
    print("SENT")


class Batch:
    def __init__(self, session: Session, logger: object = None):
        self.__session = session
        self.__batch = session.batch_manual()
        self.__cas_keys = []
        self.logger = logger

    def batch(self):
        return self.__batch

    def send_sync(self):
        for entry in self.__cas_keys:
            self.cas_sync(**entry)

        asyncio.get_event_loop().run_until_complete(send_batch(self.__batch, self.logger))

    async def send(self):
        for entry in self.__cas_keys:
            entry_cas = await KVClient.get_entry_with_version(self.__session, **entry)
            new_value = entry.get('new_value')
            entry_cas.cas(new_value=new_value, batch=self.__batch)

        await send_batch(self.__batch, self.logger)

    def set(self, partition_key: List[str], new_value: object, clustering_key: Optional[List[str]] = None):
        entry = self.__session.entry(partition_key, clustering_key)
        entry.set(new_value=new_value, batch=self.__batch)

    def set_sync(self, partition_key: List[str], new_value: object, clustering_key: Optional[List[str]] = None):
        asyncio.get_event_loop().run_until_complete(
            self.set(partition_key, new_value, clustering_key)
        )

    def add_to_cas_keys(self, partition_key: List[str], new_value: object,
                        clustering_key: Optional[List[str]] = None, version: Optional[int] = None):
        entry = None
        for e in self.__cas_keys:
            if e['partition_key'] == partition_key and e['clustering_key'] == clustering_key:
                entry = e
                break

        if not entry:
            entry = {
                'partition_key': partition_key,
                'version': version,
                'clustering_key': clustering_key
            }
            self.__cas_keys += [entry]

        entry['new_value'] = new_value


batches = {}
batch_id = 0


class KVClient:
    def __init__(self, session: Session, logger: object):
        self._batch = None
        self._session = session
        self.logger = logger

    @staticmethod
    def session(host, port, read_timeout: Optional[int] = 10) -> Session:
        session = Session(
            host=host,
            port=port,
            api_prefix=''  # empty for rf version of kv
        )

        # по-умочанию read_timeout aiohttp - 5 минут, что в данном случае весьма много
        session._session._session._timeout = aiohttp.ClientTimeout(total=2 * read_timeout)

        return session

    @staticmethod
    @with_retries(success_max=1)
    async def get_entry(session: Session, partition_key: List[str], clustering_key: Optional[List[str]] = None,
                        logger: object = None):
        return await session.get_entry(
            partition=partition_key,
            clustering=clustering_key
        )

    @staticmethod
    async def get_entry_with_version(
            session: Session,
            partition_key: List[str],
            clustering_key: Optional[List[str]] = None,
            version: Optional[int] = None,
            **kwargs
    ):
        entry_version = version
        if entry_version is None:
            entry = await KVClient.get_entry(session, partition_key, clustering_key)
            entry_version = entry._version

        entry_res = session.entry(partition_key, clustering_key)
        entry_res._version = entry_version

        return entry_res

    @staticmethod
    def make_batch(session: Session, logger: object = None) -> int:
        global batch_id
        global batches

        _batch_id = batch_id
        batches[_batch_id] = Batch(session, logger)
        batch_id += 1
        return _batch_id

    @staticmethod
    def get_batch(b_id: int) -> Batch:
        global batches
        try:
            return batches[b_id]
        except KeyError:
            raise BatchDoesNotExist()

    @staticmethod
    def remove_batch(b_id: int):
        global batches
        try:
            del batches[b_id]
        except KeyError:
            raise BatchDoesNotExist()

    @staticmethod
    async def execute_batch(b_id: int):
        global batches

        if b_id not in batches:
            return

        batch = batches[b_id]
        print('EXECUTING BATCH')

        try:
            await batch.send()
        except Exception:
            raise BatchSendError()
        finally:
            del batches[b_id]

    @staticmethod
    def execute_batch_sync(b_id: int):
        global batches

        if b_id not in batches:
            return

        batch = batches[b_id]

        try:
            batch.send_sync()
        except Exception:
            raise BatchSendError()
        finally:
            del batches[b_id]

    @contextmanager
    def batch(self):
        try:
            self._batch = Batch(self._session)
            yield self._batch
            self._batch.send_sync()
        except Exception as e:
            if self.logger:
                self.logger.error(e)
            raise BatchSendError()
        finally:
            pending = asyncio.Task.all_tasks()
            asyncio.get_event_loop().run_until_complete(asyncio.gather(*pending))

    def __enter__(self):
        self._batch = Batch(self._session)
        return self._batch

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self._batch.send_sync()
        except Exception as e:
            if self.logger:
                self.logger.error(e)

    async def __aenter__(self):
        self._batch = Batch(self._session)
        return self._batch

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self._batch.send()
        except Exception as e:
            if self.logger:
                self.logger.error(e)

    @staticmethod
    async def listen(session: Session, partition_key: List[str], clustering_key: Optional[List[str]],
                     action: Callable, timeout: Optional[int]=3, logger: Optional[object] = None, backoff: int = 2):
        @with_retries(
            backoff=backoff, logger=logger, partition_key=partition_key, clustering_key=clustering_key
        )
        async def listen_for(entry, action):
            await entry.listen(timeout=timedelta(seconds=timeout))

            if asyncio.iscoroutinefunction(action):
                await action(entry.value, entry.partition, entry.clustering)
            else:
                action(entry.value, entry.partition, entry.clustering)

        if not action:
            if logger:
                logger.error('no action, listen is pointless')
            return

        entry = session.entry(
            partition_key if type(partition_key) == list else partition_key.split(':'),
            clustering_key if type(clustering_key) == list else clustering_key.split(':') if clustering_key else None
        )

        # noinspection PyAsyncCall
        return asyncio.ensure_future(listen_for(entry, action))

    @staticmethod
    def timestamp(time: Optional[str]=None):
        return str(int((dateutil.parser.parse(time) if time else datetime.now()).timestamp() * 1000))

    @staticmethod
    def to_kv_timestamp(timestamp: Optional[str] = None):
        return str(int((dateutil.parser.parse(timestamp) if timestamp else datetime.now()).timestamp() * 1000))

    @staticmethod
    def from_kv_timestamp(timestamp: Optional[str] = None):
        return datetime.fromtimestamp(int(timestamp) / 1000) if timestamp else datetime.now()
