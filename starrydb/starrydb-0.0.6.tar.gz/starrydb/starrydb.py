#
# Copyright (c) 2018, BWStor, Inc. <www.bwstor.com.cn>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the authors nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL ANDRES MOREIRA BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""starrydb.py

starrydb module provide functions of a NoSQL database for lightweight data.

"""

import os
import signal
import time
import shutil
import msgpack
import stat
import pylibmc
import inspect
import threading
import logging
import multiprocessing.connection
import concurrent.futures
from contextlib import contextmanager

VERSION = "0.0.6"

class StarryError(Exception):
    def __init__(self, output):
        self.output = output

class StarryLog(object):
    def __init__(self, file=None, lvl=logging.NOTSET):
        self.__logger = None

        if os.path.isfile(file):
            try:
                logging.basicConfig(
                    handlers=[logging.FileHandler(file)],
                    format=f"%(asctime)s <%(levelname)s> {inspect.stack()[-1][1].split('/')[-1]}[%(process)d]: %(message)s",
                    level=lvl)

                self.__logger = logging.getLogger()
            except:
                self.__logger = None

    def debug(self, msg):
        if self.__logger is None:
            return None

        try:
            caller = inspect.stack()
            self.__logger.debug(f"[{caller[1][1].split('/')[-1]}:{caller[1][2]}] {msg}")
        except:
            pass

    def info(self, msg):
        if self.__logger is None:
            return None

        try:
            caller = inspect.stack()
            self.__logger.info(f"[{caller[1][1].split('/')[-1]}:{caller[1][2]}] {msg}")
        except:
            pass

    def warn(self, msg):
        if self.__logger is None:
            return None

        try:
            caller = inspect.stack()
            self.__logger.warning(f"[{caller[1][1].split('/')[-1]}:{caller[1][2]}] {msg}")
        except:
            pass

    def warning(self, msg):
        self.warn(msg)

    def error(self, msg):
        if self.__logger is None:
            return None

        try:
            caller = inspect.stack()
            self.__logger.error(f"[{caller[1][1].split('/')[-1]}:{caller[1][2]}] {msg}")
        except:
            pass

    def fatal(self, msg):
        if self.__logger is None:
            return None

        try:
            caller = inspect.stack()
            self.__logger.critical(f"[{caller[1][1].split('/')[-1]}:{caller[1][2]}] {msg}")
        except:
            pass

    def exception(self, msg):
        if self.__logger is None:
            return None

        try:
            caller = inspect.stack()
            self.__logger.exception(f"[{caller[1][1].split('/')[-1]}:{caller[1][2]}] {msg}")
        except:
            pass

class LibMemcachedClient(pylibmc.ThreadMappedPool):
    '''This module supplies a client in Python for memcached based on libmemcached.'''

    def __init__(self, addr):
        mc = pylibmc.Client([addr], behaviors={"hash": "crc"})

        try:
            mc.get_stats()
        except:
            mc.flush_all()
            raise StarryError("init pylibmc.Client() failed.")

        super().__init__(mc)

    def flush_all(self):
        with self.reserve() as mc:
            return mc.flush_all()

    def get(self, key):
        with self.reserve() as mc:
            return mc.get(key)

    def set(self, key, value, time=0):
        with self.reserve() as mc:
            if mc.set(key, value, time=time) is False:
                mc.delete(key)
                return False

        return True

    def delete(self, key):
        with self.reserve() as mc:
            return mc.delete(key)

class StarryServer(object):
    def __init__(self, database, address, cache=64, log=None):
        self.database = os.path.abspath(database)

        if not os.path.isdir(self.database):
            os.mkdir(self.database)

        if type(address) is str:
            _removeFile(address)

        self.address = address
        self.cache = None

        if int(cache) > 0:
            try:
                os.system("kill -9 $(ps -ef | grep " + os.path.join(self.database, 'cache.sock') + " | awk '$0 !~/grep/ {print $2}') 2>/dev/null")
            except:
                pass

            try:
                os.system(f"memcached -d -u root -a 0777 -D : -C -m {int(cache)} -s {os.path.join(self.database, 'cache.sock')}")

                time.sleep(1)

                self.cache = LibMemcachedClient(os.path.join(self.database, "cache.sock"))
            except:
                try:
                    os.system("kill -9 $(ps -ef | grep " + os.path.join(self.database, 'cache.sock') + " | awk '$0 !~/grep/ {print $2}') 2>/dev/null")
                except:
                    pass

                self.cache = None

        self.logger = StarryLog(log) if log is not None else None
        self.thread_cond = threading.Condition()
        self.thread_lock = threading.RLock()
        self.queue = []

        backup_dir = os.path.join(self.database, ".backup/")

        if not os.path.isdir(backup_dir):
            os.mkdir(backup_dir)
            os.mknod(os.path.join(backup_dir, "~.lock"))
            self.backup()

    def __del__(self):
        if self.cache is not None:
            try:
                os.system("kill -9 $(ps -ef | grep " + os.path.join(self.database, 'cache.sock') + " | awk '$0 !~/grep/ {print $2}') 2>/dev/null")
            except:
                pass

    def start(self, max_workers=512, backlog=512, authkey=b'starry'):
        with multiprocessing.connection.Listener(self.address, backlog=backlog, authkey=authkey) as listener:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                def _terminate(signum, frame):
                    try:
                        listener.close()
                    except:
                        pass

                    try:
                        executor.shutdown()
                    except:
                        pass

                signal.signal(signal.SIGTERM, _terminate)

                while True:
                    try:
                        conn = listener.accept()
                    except OSError as e:
                        self.logger.warn(f"Caught exception: {e.__class__}({e})")
                        break
                    except Exception as e:
                        self.logger.warn(f"Caught exception: {e.__class__}({e})")
                        continue

                    try:
                        tlock = conn.recv()
                        executor.submit(self._callableForward, conn, tlock)
                    except Exception as e:
                        self.logger.error(f"Caught exception: {e.__class__}({e})")

                        try:
                            conn.close()
                        except:
                            pass

    def _callableForward(self, conn, tlock=False):
        if tlock is False:
            while True:
                try:
                    (func, *param) = conn.recv()
                except:
                    break

                try:
                    conn.send(eval(f"self.{func}")(*param))
                except Exception as e:
                    self.logger.debug(f"Caught exception: {e.__class__}({e})")

                    try:
                        conn.send((False, f"Caught exception: {e.__class__}({e})"))
                    except:
                        pass

                    break
        else:
            with self.thread_lock:
                while True:
                    try:
                        (func, *param) = conn.recv()
                    except:
                        break

                    try:
                        conn.send(eval(f"self.{func}")(*param))
                    except Exception as e:
                        self.logger.debug(f"Caught exception: {e.__class__}({e})")

                        try:
                            conn.send((False, f"Caught exception: {e.__class__}({e})"))
                        except:
                            pass

                        break

        if self.cache is not None:
            try:
                self.cache.relinquish()
            except:
                pass

        try:
            conn.close()
        except:
            pass

    def get(self, key):
        if type(key) is not list:
            key = [key]

        mark = {"mode": "r", "members": [key[0][0]] if type(key[0]) is tuple else [key[0]]}

        with self._lock(mark):
            return self._get(key)

    def update(self, key, value):
        if type(key) is not list:
            key = [key]

        mark = {"mode": "w", "members": [key[0]]}

        with self._lock(mark):
            return self._update(key, value)

    def insert(self, key, value):
        if type(key) is not list:
            key = [key]

        mark = {"mode": "w", "members": [key[0]]}

        with self._lock(mark):
            return self._insert(key, value)

    def delete(self, key):
        if type(key) is not list:
            key = [key]

        mark = {"mode": "w", "members": [key[0]]}

        with self._lock(mark):
            return self._delete(key)

    def clone(self, old_key, new_key):
        mark = {"mode": "w", "members": [old_key, new_key]}

        with self._lock(mark):
            (ret, value) = self._get([old_key])
            if ret is False:
                return (ret, value)

            return self._insert([new_key], value)

    def rename(self, old_key, new_key):
        mark = {"mode": "w", "members": [old_key, new_key]}

        with self._lock(mark):
            (ret, value) = self._get([old_key])
            if ret is False:
                return (ret, value)

            (ret, msg) = self._insert([new_key], value)
            if ret is False:
                return (ret, msg)

            (ret, msg) = self._delete([old_key])
            if ret is False:
                self._delete([new_key])

            return (ret, msg)

    def exist(self, key):
        if type(key) is not list:
            key = [key]

        mark = {"mode": "r", "members": [key[0][0]] if type(key[0]) is tuple else [key[0]]}

        with self._lock(mark):
            (ret, _) = self._get(key)
            return (True, ret)

    def getMultiList(self, keys):
        values = []

        mark = {"mode": "r", "members": keys}

        with self._lock(mark):
            for key in keys:
                (ret, value) = self._get([key])
                if ret is False:
                    return (ret, value)

                values.append(value)

            return (True, values)

    def getMultiDict(self, keys):
        values = {}

        mark = {"mode": "r", "members": keys}

        with self._lock(mark):
            for key in keys:
                (ret, value) = self._get([key])
                if ret is False:
                    return (ret, value)

                values[key] = value

            return (True, values)

    def updateMulti(self, values):
        mark = {"mode": "w", "members": list(values.keys())}

        with self._lock(mark):
            for key, value in values.items():
                (ret, msg) = self._update([key], value)
                if ret is False:
                    return (ret, msg)

            return (True, "")

    def insertMulti(self, values):
        mark = {"mode": "w", "members": list(values.keys())}

        with self._lock(mark):
            for key, value in values.items():
                (ret, msg) = self._insert([key], value)
                if ret is False:
                    return (ret, msg)

            return (True, "")

    def deleteMulti(self, keys):
        mark = {"mode": "w", "members": keys}

        with self._lock(mark):
            for key in keys:
                (ret, msg) = self._delete([key])
                if ret is False:
                    return (ret, msg)

            return (True, "")

    def list(self):
        mark = {"mode": "r", "members": [None]}

        with self._lock(mark):
            return (True, [elem.name.replace('.mpb', '') for elem in os.scandir(self.database) if elem.name.endswith(".mpb")])

    def getAll(self):
        values = {}

        mark = {"mode": "r", "members": [None]}

        with self._lock(mark):
            for key in [elem.name.replace('.mpb', '') for elem in os.scandir(self.database) if elem.name.endswith(".mpb")]:
                (ret, value) = self._get([key])
                if ret is False:
                    return (ret, value)

                values[key] = value

            return (True, values)

    def updateAll(self, values):
        mark = {"mode": "w", "members": [None]}

        with self._lock(mark):
            keys = [elem.name.replace('.mpb', '') for elem in os.scandir(self.database) if elem.name.endswith(".mpb")]

            for key, value in values.items():
                if key in keys:
                    (ret, msg) = self._update([key], value)
                    if ret is False:
                        return (ret, msg)
                else:
                    (ret, msg) = self._insert([key], value)
                    if ret is False:
                        return (ret, msg)

            for key in keys:
                if key not in values:
                    self._delete([key])

            return (True, "")

    def backup(self):
        mark = {"mode": "w", "members": [None]}

        with self._lock(mark):
            for key in [elem.name.replace('.mpb', '') for elem in os.scandir(self.database) if elem.name.endswith(".mpb")]:
                (ret, msg) = self._backup(key)
                if ret is False:
                    return (ret, msg)

            return (True, "")

    def recover(self):
        mark = {"mode": "w", "members": [None]}

        with self._lock(mark):
            keys = [elem.name.replace('.mpb', '') for elem in os.scandir(self.database) if elem.name.endswith(".mpb")]
            backup_keys = [elem.name.replace('.mpb', '') for elem in os.scandir(f"{self.database}/.backup") if elem.name.endswith(".mpb")]

            for key in backup_keys:
                if key not in keys:
                    keys.append(key)

            for key in keys:
                (ret, msg) = self._get([key])
                if ret is False:
                    self._recover(key)

            return (True, "")

    def save(self, path):
        path = os.path.abspath(path)

        if not os.path.isdir(path):
            self.logger.error(f"No {path}.")
            return (False, f"No {path}.")

        for elem in os.scandir(path):
            if elem.name.endswith(".mpb"):
                _removeFile(elem.path)
                _removeFile(f"{elem.path}.tmp")

        mark = {"mode": "w", "members": [None]}

        with self._lock(mark):
            for key in [elem.name.replace('.mpb', '') for elem in os.scandir(self.database) if elem.name.endswith(".mpb")]:
                (ret, msg) = self._backup(key, path=path)
                if ret is False:
                    return (ret, msg)

            return (True, "")

    def load(self, path):
        path = os.path.abspath(path)

        if not os.path.isdir(path):
            self.logger.error(f"No {path}.")
            return (False, f"No {path}.")

        files = [elem.name.replace('.mpb', '') for elem in os.scandir(path) if elem.name.endswith(".mpb")]

        mark = {"mode": "w", "members": [None]}

        with self._lock(mark):
            for key in files:
                (ret, msg) = self._load(key, path)
                if ret is False:
                    return (ret, msg)

            for key in [elem.name.replace('.mpb', '') for elem in os.scandir(self.database) if elem.name.endswith(".mpb")]:
                if key not in files:
                    self._delete([key])

            return (True, "")

    def replace(self, path):
        path = os.path.abspath(path)

        if not os.path.isdir(path):
            self.logger.error(f"No {path}.")
            return (False, f"No {path}.")

        files = [elem.name.replace('.mpb', '') for elem in os.scandir(path) if elem.name.endswith(".mpb")]

        mark = {"mode": "w", "members": [None]}

        with self._lock(mark):
            for key in files:
                (ret, msg) = self._load(key, path)
                if ret is False:
                    return (ret, msg)

            for key in [elem.name.replace('.mpb', '') for elem in os.scandir(self.database) if elem.name.endswith(".mpb")]:
                if key not in files:
                    self._delete([key])

            for key in files:
                _removeFile(os.path.join(path, f"{key}.mpb"))

            return (True, "")

    def upgrade(self, path):
        path = os.path.abspath(path)

        if not os.path.isdir(path):
            self.logger.error(f"No {path}.")
            return (False, f"No {path}.")

        files = [elem.name.replace('.mpb', '') for elem in os.scandir(path) if elem.name.endswith(".mpb")]

        mark = {"mode": "w", "members": [None]}

        with self._lock(mark):
            for key in files:
                (ret, msg) = self._load(key, path)
                if ret is False:
                    return (ret, msg)

            return (True, "")

    def clear(self):
        for elem in os.scandir(self.database):
            if elem.is_file():
                (ret, msg) = _removeFile(elem.path)
                if ret is False:
                    self.logger.error(msg)
                    return (ret, msg)
            elif elem.isdir():
                try:
                    shutil.rmtree(elem.path)
                except Exception as e:
                    self.logger.error(f"Caught exception: {e.__class__}({e})")
                    return (False, f"Caught exception: {e.__class__}({e})")

        try:
            self.cache.flush_all()
        except:
            pass

        self.queue.clear()

        return (True, "")

    def destroy(self):
        if os.path.isdir(self.database):
            try:
                shutil.rmtree(self.database)
            except Exception as e:
                self.logger.error(f"Caught exception: {e.__class__}({e})")
                return (False, f"Caught exception: {e.__class__}({e})")

        self.clear()
        self = []

        return (True, "")

    def _getCache(self, key):
        if self.cache is None:
            return None

        try:
            value = self.cache.get(key)
        except:
            return None

        if value is None:
            return None

        try:
            value = msgpack.loads(value, raw=False)
        except:
            try:
                self.cache.delete(key)
            except:
                pass

            return None

        return value

    def _setCache(self, key, value):
        if self.cache is not None:
            try:
                self.cache.set(key, value)
            except:
                return False

        return True

    def _deleteCache(self, key):
        if self.cache is not None:
            try:
                self.cache.delete(key)
            except:
                return False

        return True

    def _get(self, route):
        branch = route[:]
        key = branch.pop(0)
        filters = []

        if type(key) is tuple:
            (key, filters) = key

            if type(filters) is not list:
                filters = [filters]

        file = os.path.join(self.database, f"{key}.mpb")

        value = self._getCache(key)
        if value is None:
            (ret, data) = _readFile(file)
            if ret is False:
                return (ret, data)

            try:
                value = msgpack.loads(data, raw=False)
                self._setCache(key, data)
            except:
                (ret, value) = self._recover(key)
                if ret is False:
                    return (ret, value)

        if len(branch) > 0:
            (ret, value) = _getPart(value, branch, filters)
            if ret is False:
                return (False, f'Can not find {"~".join(branch)} in {key}.')

        return (True, value)

    def _update(self, route, part):
        branch = route[:]
        key = branch.pop(0)
        file = os.path.join(self.database, f"{key}.mpb")
        backup = os.path.join(self.database, ".backup/", f"{key}.mpb")

        if len(branch) == 0:
            if not os.path.exists(file):
                try:
                    os.mknod(file)
                except Exception as e:
                    _removeFile(file)
                    return (False, f"Caught exception: {e.__class__}({e})")
            elif self._getCache(key) == part:
                return (True, "")

            value = part
        else:
            if not os.path.exists(file):
                return (False, f"No {key}.")

            if not os.path.exists(backup):
                (ret, msg) = self._backup(key)
                if ret is False:
                    return (ret, msg)

            (ret, value) = _readFile(file)
            if ret is False:
                return (ret, value)

            try:
                value = msgpack.loads(value, raw=False)
            except Exception as e:
                self._recover(key)
                return (False, f"Caught exception: {e.__class__}({e})")

            (ret, msg) = _updatePart(value, branch, part)
            if ret is False:
                return (False, f"Update {key} failed: {msg}")
            elif msg is False:
                return (True, "")

        try:
            value = msgpack.dumps(value, use_bin_type=True)
        except Exception as e:
            return (False, f"Caught exception: {e.__class__}({e})")

        (ret, msg) = _writeFile(file, value)
        if ret is False:
            self._recover(key)
            return (ret, msg)

        self._setCache(key, value)

        return self._backup(key, check_flag=False)

    def _insert(self, route, part):
        branch = route[:]
        key = branch.pop(0)
        file = os.path.join(self.database, f"{key}.mpb")
        backup = os.path.join(self.database, ".backup/", f"{key}.mpb")

        if len(branch) == 0:
            value = part
        else:
            if not os.path.exists(file):
                return (False, f"No {key}.")

            if not os.path.exists(backup):
                (ret, msg) = self._backup(key)
                if ret is False:
                    return (ret, msg)

            (ret, value) = _readFile(file)
            if ret is False:
                return (ret, value)

            try:
                value = msgpack.loads(value, raw=False)
            except Exception as e:
                self._recover(key)
                return (False, f"Caught exception: {e.__class__}({e})")

            (ret, msg) = _insertPart(value, branch, part)
            if ret is False:
                return (False, f"Insert {key} failed: {msg}")
            elif msg is False:
                return (True, "")

        try:
            value = msgpack.dumps(value, use_bin_type=True)
        except Exception as e:
            return (False, f"Caught exception: {e.__class__}({e})")

        if not os.path.exists(file):
            try:
                os.mknod(file)
            except Exception as e:
                _removeFile(file)
                return (False, f"Caught exception: {e.__class__}({e})")

        (ret, msg) = _writeFile(file, value)
        if ret is False:
            self._recover(key)
            return (ret, msg)

        self._setCache(key, value)

        return self._backup(key, check_flag=False)

    def _delete(self, route):
        branch = route[:]
        key = branch.pop(0)
        file = os.path.join(self.database, f"{key}.mpb")
        backup = os.path.join(self.database, ".backup/", f"{key}.mpb")

        if not os.path.exists(file):
            self._deleteCache(key)

            _removeFile(f"{file}.tmp")

            if len(branch) == 0:
                _removeFile(backup)
                _removeFile(f"{backup}.tmp")
                return (True, "")
            else:
                self._recover(key)
                return (False, f"No {key}.")

        if not os.path.exists(backup):
            (ret, msg) = self._backup(key)
            if ret is False:
                return (ret, msg)

        if len(branch) == 0:
            self._deleteCache(key)

            _removeFile(f"{file}.tmp")

            (ret, msg) = _removeFile(file)
            if ret is False:
                self._recover(key)
                return (False, msg)

            _removeFile(backup)
            _removeFile(f"{backup}.tmp")

            return (True, "")

        (ret, value) = _readFile(file)
        if ret is False:
            return (ret, value)

        try:
            value = msgpack.loads(value, raw=False)
        except Exception as e:
            self._recover(key)
            return (False, f"Caught exception: {e.__class__}({e})")

        (ret, msg) = _deletePart(value, branch)
        if ret is False:
            return (False, f"Delete {key} failed: {msg}")

        try:
            value = msgpack.dumps(value, use_bin_type=True)
        except Exception as e:
            return (False, f"Caught exception: {e.__class__}({e})")

        (ret, msg) = _writeFile(file, value)
        if ret is False:
            self._recover(key)
            return (ret, msg)

        self._setCache(key, value)

        return self._backup(key, check_flag=False)

    def _backup(self, key, check_flag=True, path=None):
        file = os.path.join(self.database, f"{key}.mpb")

        if path is None:
            backup = os.path.join(self.database, ".backup/", f"{key}.mpb")
        else:
            backup = os.path.join(path, f"{key}.mpb")

        if not os.path.exists(file):
            return (False, f"No {key}.")

        if check_flag is True:
            (ret, data) = _readFile(file)
            if ret is False:
                return (ret, data)

            try:
                msgpack.loads(data, raw=False)
            except Exception as e:
                self._recover(key)
                return (False, f"Caught exception: {e.__class__}({e})")

        return _copyFile(file, backup, statement=not os.path.exists(backup))

    def _recover(self, key):
        file = os.path.join(self.database, f"{key}.mpb")
        backup = os.path.join(self.database, ".backup/", f"{key}.mpb")

        self._deleteCache(key)

        if not os.path.exists(backup):
            return (False, f"No {backup}.")

        (ret, value) = _readFile(backup)
        if ret is False:
            return (ret, value)

        try:
            data = msgpack.loads(value, raw=True)
        except Exception as e:
            _removeFile(backup)
            _removeFile(f"{backup}.tmp")
            return (False, f"Caught exception: {e.__class__}({e})")

        (ret, msg) = _copyFile(backup, file, statement=not os.path.exists(file))
        if ret is False:
            return (ret, msg)

        self._setCache(key, value)

        return (True, data)

    def _load(self, key, path):
        file = os.path.join(self.database, f"{key}.mpb")
        source = os.path.join(path, f"{key}.mpb")
        backup = os.path.join(self.database, ".backup/", f"{key}.mpb")

        if not os.path.exists(source):
            return (False, f"No {source}.")

        (ret, value) = _readFile(source)
        if ret is False:
            return (ret, value)

        try:
            msgpack.loads(value, raw=False)
        except Exception as e:
            return (False, f"Caught exception: {e.__class__}({e})")

        if os.path.exists(file):
            if not os.path.exists(backup):
                (ret, msg) = self._backup(key)
                if ret is False:
                    return (ret, msg)

        (ret, msg) = _copyFile(source, file, statement=not os.path.exists(file))
        if ret is False:
            if not os.path.exists(backup):
                _removeFile(file)
                _removeFile(f"{file}.tmp")
                _removeFile(f"{backup}.tmp")
            else:
                self._recover(key)

            return (ret, msg)

        self._setCache(key, value)

        return self._backup(key, check_flag=False)

    @contextmanager
    def _lock(self, mark):
        def _predicate():
            if len(self.queue) > 0:
                if mark["mode"] == "r":
                    if any([q["mode"] == "w" for q in self.queue]):
                        if None in mark["members"]:
                            return False

                        if any([q["mode"] == "w" and (None in q["members"] or len(set(q["members"]) & set(mark["members"])) > 0) for q in self.queue]):
                            return False
                else:
                    if None in mark["members"]:
                        return False

                    if any([None in q["members"] or len(set(q["members"]) & set(mark["members"])) > 0 for q in self.queue]):
                        return False

            self.queue.append(mark)
            return True

        with self.thread_cond:
            self.thread_cond.wait_for(_predicate)

        yield

        with self.thread_cond:
            try:
                self.queue.remove(mark)
            except:
                pass

            self.thread_cond.notify_all()

class StarryClient(object):
    def __init__(self, address, tlock=False):
        try:
            self.client = multiprocessing.connection.Client(address, authkey=b'starry')
            self.client.send(tlock)
        except:
            raise StarryError("connect server failed.")

    def __del__(self):
        try:
            self.client.close()
        except:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__del__()

    def _callableForward(self, func, *args):
        try:
            self.client.send((func, *args))
        except Exception as e:
            return (False, f"Caught exception: {e.__class__}({e})")

        try:
            if self.client.poll(60):
                return self.client.recv()
            else:
                return (False, "timeout")
        except Exception as e:
            return (False, f"Caught exception: {e.__class__}({e})")

    def get(self, key):
        return self._callableForward("get", key)

    def update(self, key, value):
        return self._callableForward("update", key, value)

    def insert(self, key, value):
        return self._callableForward("insert", key, value)

    def delete(self, key):
        return self._callableForward("delete", key)

    def clone(self, old_key, new_key):
        return self._callableForward("clone", old_key, new_key)

    def rename(self, old_key, new_key):
        return self._callableForward("rename", old_key, new_key)

    def exist(self, key):
        return self._callableForward("exist", key)

    def list(self):
        return self._callableForward("list")

    def getEpoch(self):
        return self._callableForward("getEpoch")

    def backup(self):
        return self._callableForward("backup")

    def recover(self):
        return self._callableForward("recover")

    def save(self, path):
        return self._callableForward("save", path)

    def load(self, path):
        return self._callableForward("load", path)

    def replace(self, path):
        return self._callableForward("replace", path)

    def upgrade(self, path):
        return self._callableForward("upgrade", path)

    def clear(self):
        return self._callableForward("clear")

    def destroy(self):
        return self._callableForward("destroy")

    def getMultiList(self, keys):
        return self._callableForward("getMultiList", keys)

    def getMultiDict(self, keys):
        return self._callableForward("getMultiDict", keys)

    def getAll(self):
        return self._callableForward("getAll")

    def updateMulti(self, values):
        return self._callableForward("updateMulti", values)

    def updateAll(self, values):
        return self._callableForward("updateAll", values)

    def insertMulti(self, values):
        return self._callableForward("insertMulti", values)

    def deleteMulti(self, keys):
        return self._callableForward("deleteMulti", keys)

def _getPart(value, branch, filters):
    def _filterValue(value, filters):
        if type(value) is list:
            if any([type(v) is not dict for v in value]):
                return value

            for key in filters:
                if any([key not in v for v in value]):
                    return value

            for v in value:
                for key in list(v.keys()):
                    if key not in filters:
                        v.pop(key)

            return value
        elif type(value) is dict:
            for key in filters:
                if key not in value:
                    return value

            for key in list(value.keys()):
                if key not in filters:
                    value.pop(key)

            return value

        return value

    for knot in branch:
        branch_filters = []

        if type(knot) is tuple:
            (knot, branch_filters) = knot

            if type(branch_filters) is not list:
                branch_filters = [branch_filters]

        if type(value) is list:
            if type(knot) is int:
                try:
                    value = value[knot]
                except Exception as e:
                    return (False, f"Caught exception: {e.__class__}({e})")
            elif all([type(v) is dict for v in value]):
                try:
                    value = [v[knot] for v in value if knot in v]
                except Exception as e:
                    return (False, f"Caught exception: {e.__class__}({e})")
            else:
                return (False, f"Syntax error.")
        elif type(value) is dict and knot in value:
            value = value[knot]
        else:
            return (False, f"Syntax error.")

        if len(branch_filters) > 0:
            value = _filterValue(value, branch_filters)

    if len(filters) > 0:
        return (True, _filterValue(value, filters))

    return (True, value)

def _updatePart(value, branch, part):
    if len(branch) > 1:
        knot = branch.pop(0)

        if type(value) is list and type(knot) is int:
            knot = len(value) + knot if knot < 0 else knot

            if 0 <= knot < len(value):
                return _updatePart(value[knot], branch, part)
        elif type(value) is dict and knot in value:
            return _updatePart(value[knot], branch, part)
    elif len(branch) == 1:
        knot = branch.pop(0)

        if type(value) is list and type(knot) is int:
            knot = len(value) + knot if knot < 0 else knot

            if 0 <= knot < len(value):
                if value[knot] == part:
                    return (True, False)

                value[knot] = part
                return (True, True)
        elif type(value) is dict and knot in value:
            if value[knot] == part:
                return (True, False)

            value[knot] = part
            return (True, True)

    return (False, "Syntax error.")

def _insertPart(value, branch, part):
    if len(branch) > 1:
        knot = branch.pop(0)

        if type(value) is list and type(knot) is int:
            knot = len(value) + knot if knot < 0 else knot

            if 0 <= knot <= len(value):
                return _insertPart(value[knot], branch, part)
        elif type(value) is dict and knot in value:
            return _insertPart(value[knot], branch, part)
    elif len(branch) == 1:
        knot = branch.pop(0)

        if type(value) is list and type(knot) is int:
            knot = len(value) + knot if knot < 0 else knot

            if 0 <= knot <= len(value):
                value.insert(knot, part)
                return (True, "")
        elif type(value) is dict:
            if knot in value and value[knot] == part:
                return (True, False)

            value[knot] = part
            return (True, True)

    return (False, "Syntax error.")

def _deletePart(value, branch):
    if len(branch) > 1:
        knot = branch.pop(0)

        if type(value) is list and type(knot) is int:
            knot = len(value) + knot if knot < 0 else knot

            if 0 <= knot < len(value):
                return _deletePart(value[knot], branch)
        elif type(value) is dict and knot in value:
            return _deletePart(value[knot], branch)
    elif len(branch) == 1:
        knot = branch.pop(0)

        if type(value) is list and type(knot) is int:
            knot = len(value) + knot if knot < 0 else knot

            if 0 <= knot < len(value):
                value.pop(knot)
                return (True, "")
        elif type(value) is dict and knot in value:
            value.pop(knot)
            return (True, "")

    return (False, "Syntax error.")

def _readFile(src):
    try:
        with open(src, "rb") as descriptor:
            value = descriptor.read()
    except Exception as e:
        return (False, f"Caught exception: {e.__class__}({e})")

    return (True, value)

def _writeFile(dst, value):
    try:
        with open(dst, "wb", buffering=0) as descriptor:
            descriptor.write(value)
            descriptor.truncate()

            descriptor.flush()
            os.fdatasync(descriptor.fileno())

        if len(value) != os.path.getsize(dst):
            return (False, "No space left on device.")
    except Exception as e:
        return (False, f"Caught exception: {e.__class__}({e})")

    return (True, "")

def _removeFile(file):
    try:
        if os.path.exists(file):
            os.remove(file)
    except Exception as e:
        return (False, f"Caught exception: {e.__class__}({e})")

    return (True, "")

def _copyFile(src, dst, statement=False):
    (ret, value) = _readFile(src)
    if ret is False:
        return (ret, value)

    if statement is True:
        try:
            st = os.stat(src)
        except:
            statement = False

    tmp_file = None

    if os.path.exists(dst):
        tmp_file = f"{dst}.tmp"
    else:
        (ret, msg) = _writeFile(dst, value)
        if ret is False:
            _removeFile(dst)
            return (ret, msg)

    if tmp_file is not None:
        (ret, msg) = _writeFile(tmp_file, value)
        if ret is False:
            _removeFile(tmp_file)
            return (ret, msg)

        try:
            os.rename(tmp_file, dst)
        except:
            _removeFile(tmp_file)

            (ret, msg) = _writeFile(dst, value)
            if ret is False:
                return (ret, msg)

    if statement is True:
        try:
            os.chmod(dst, stat.S_IMODE(st.st_mode))
            os.chown(dst, st.st_uid, st.st_gid)
        except:
            pass

    return (True, "")
