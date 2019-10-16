
class LakaService(object):

    def __init__(self, name, redis_host, redis_port, queue, redis_db=0):
        self.name = name
        self.queue = queue
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db

    @classmethod
    def load_from_json(cls, data):
        if not isinstance(data, dict):
            raise MakeServiceError("data type should be dict, but {} found".format(type(data)))
        name = data.get("Service")
        # host = data.get("Address")
        # port = data.get("Port")
        meta = data.get("Meta")
        if not isinstance(meta, dict):
            raise MakeServiceError("meta type should be dict, but {} found".format(type(meta)))
        queue = meta.get("queue")
        redis_host = meta.get("redis_host")
        redis_port = int(meta.get("redis_port"))
        redis_db = int(meta.get("redis_db", 0))
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
            "Name": self.name,
            # "Port": 0, 
            "Meta": {
                "redis_host": self.redis_host,
                "redis_port": str(self.redis_port),
                "redis_db": str(self.redis_db),
                "queue": self.queue
            },
            # "Address": "",
        }
        return r
        