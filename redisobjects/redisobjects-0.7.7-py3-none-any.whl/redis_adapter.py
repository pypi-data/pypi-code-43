'''
The RedisAdapter class is used to adapt to synchronoous Redis APIs that do not have a generic
execute method, but do have 1:1 methods for each Redis command.
'''
class RedisAdapter:
    def __init__(self, redis):
        self.redis = redis

    async def execute(self, *args):
        if len(args) == 0:
            pass
        method_name = args[0]
        if method_name == 'del':
            method_name = 'delete'
        method = getattr(self.redis, method_name)
        if method is None:
            raise LookupError('Method was not found for the given Redis API implementation.')
        return method(*args[1:])
