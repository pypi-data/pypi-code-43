from .redis_atom import RedisAtom
from .serializers import GenericSerializer

'''
A RedisInteger is a RedisAtom with an integer as its value and additional methods
for manipulating integers.
'''
class RedisInteger(RedisAtom):
    def __init__(self, *, connection=None, key=None):
        RedisAtom.__init__(self, connection=connection, key=key, serializer=GenericSerializer(int)) # <--- Serializing ints to strings causes it to fail?

    '''
    Increment the integer.
    :param int n
    :param RedisTransaction tx
    :returns boolean
    '''
    async def increment(self, *, n=1, tx=None):
        tx = tx or self.connection
        if n == 1:
            return await tx.execute('incr', self.key)
        else:
            return await tx.execute('incrby', self.key, n)

    '''
    Decrement the integer.
    :param int n
    :param RedisTransaction tx
    :returns boolean
    '''
    async def decrement(self, *, n=1, tx=None):
        tx = tx or self.connection
        if n == 1:
            return await tx.execute('decr', self.key)
        else:
            return await tx.execute('decrby', self.key, n)
