from threading import Lock


class LockUtils(object):

    def __init__(self):
        self.lock = Lock()
        self.locks = {}


    def get_lock(self, key):
        '''
        获得商家锁
        :param key:
        :return:
        '''
        with self.lock:
            if key not in self.locks.keys():
                self.locks[key] = Lock()
            return self.locks[key]

lock_utils = LockUtils()