import boto3
import threading


class AWSSession(object):

    def __init__(self, profile_name, region_name=None):
        self.profile_name = profile_name
        self.region_name = region_name
        self._thread_local = threading.local()
        self._thread_local.boto3_sessions = dict()
        self._thread_local.cache = dict()

    def __session(self):
        sessions = self._thread_local.boto3_sessions
        session_key = '{}.{}'.format(
            self.region_name,
            self.profile_name
        )

        if session_key not in sessions:
            # print("[{}] session.Session(): key={}".format(threading.get_ident(), session_key))
            if self.profile_name in boto3.session.Session().available_profiles:
                if self.region_name:
                    sessions[session_key] = boto3.session.Session(
                        profile_name=self.profile_name,
                        region_name=self.region_name
                    )
                else:
                    sessions[session_key] = boto3.session.Session(
                        profile_name=self.profile_name)
            else:
                sessions[session_key] = boto3.session.Session()

        return sessions[session_key]

    def client(self, name):
        return self.__session().client(name)

    def resource(self, name):
        return self.__session().resource(name)

    def cache(self, key, value=None):
        if value:
            cache = self._thread_local.cache
            cache[key] = value
            return value
        else:
            cache = self._thread_local.cache
            return cache.get(key, None)
