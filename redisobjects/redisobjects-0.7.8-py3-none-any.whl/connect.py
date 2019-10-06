from aioredis import create_connection
import fakeredis

from .redis_manager import RedisManager
from .redis_adapter import RedisAdapter

'''
Create a new Redis connection.
:param string address
:param dict **kwargs
:returns RedisManager
'''
async def connect(address, **kwargs):
    connection = await create_connection(address, **kwargs)
    redis_manager = RedisManager(connection)
    return redis_manager

def connect_adapter(redis):
    return RedisManager(RedisAdapter(redis))

def connect_fakeredis():
    return RedisManager(RedisAdapter(fakeredis.FakeStrictRedis()))
