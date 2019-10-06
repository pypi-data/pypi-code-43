'''
A RedisObject can be seen as a single key in a Redis database with a certain
structure (atomic, hash, list, etc.) and convenient methods that correspond
to Redis operations.
'''
class RedisObject:
    def __init__(self, *, connection=None, key=None):
        self.connection = connection
        self.key = key

    '''
    Watch this RedisObject.
    :param RedisTransaction tx
    :returns boolean
    '''
    async def watch(self, *, tx=None):
        tx = tx or self.connection
        return await tx.execute('watch', self.key)

    '''
    Unwatch this RedisObject.
    :param RedisTransaction tx
    :returns boolean
    '''
    async def unwatch(self, *, tx=None):
        tx = tx or self.connection
        return await tx.execute('unwatch', self.key)

    '''
    Delete the key that belongs to this RedisObject and thereby the RedisObject itself.
    :param RedisTransaction tx
    :returns boolean
    '''
    async def delete(self, *, tx=None):
        tx = tx or self.connection
        return await tx.execute('del', self.key)

    '''
    Expire the key after the given duration.
    :param int duration
    :returns boolean
    '''
    async def expire(self, duration, *, tx=None):
        tx = tx or self.connection
        return await tx.execute('expire', self.key, duration)
