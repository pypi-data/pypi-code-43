from .errors import MakeServiceError


class LakaService(object):

    def __init__(self, name, redis_host, redis_port, queue, redis_db=0):
        self.name = name
        self.queue = queue
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db

    @classmethod
    def load_from_json(cls, data):
        if not data:
            return None
        if not isinstance(data, dict):
            raise MakeServiceError("data type should be dict, but {} found".format(type(data)))
        name = data.get("name")
        # host = data.get("Address")
        # port = data.get("Port")
        extra = data.get("extra", {})
        if not isinstance(extra, dict):
            raise MakeServiceError("extra type should be dict, but {} found".format(type(extra)))
        queue = extra.get("queue")
        redis_host = extra.get("redis_host")
        redis_port = int(extra.get("redis_port"))
        redis_db = int(extra.get("redis_db", 0))
        if not name:
            raise MakeServiceError("name is necessary for service")
        if not redis_host:
            raise MakeServiceError("host is necessary for service")
        if not redis_port:
            raise MakeServiceError("port is necessary for service")
        if not queue:
            raise MakeServiceError("queue is necessary for service")
        return cls(name, redis_host, redis_port, queue, redis_db)
    
    def json(self):
        r = {
            "name": self.name,
            "extra": {
                "redis_host": self.redis_host,
                "redis_port": str(self.redis_port),
                "redis_db": str(self.redis_db),
                "queue": self.queue
            },
        }
        return r
        