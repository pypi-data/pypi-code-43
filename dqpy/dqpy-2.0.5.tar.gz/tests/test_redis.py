import threading
import unittest
from time import sleep
from uuid import uuid4

from dq.redis import init_redis, Redis


class TestRedis(unittest.TestCase):

    def test_init(self):
        assert init_redis('redis')
        assert not init_redis('none')
        assert not init_redis('faulty_redis')

    def test_exists(self):
        key = 'dqtest-{}'.format(uuid4())
        assert not Redis.exists(key)
        Redis.set(key, '1')
        assert Redis.exists(key)
        assert Redis.delete(key)
        assert not Redis.exists(key)

    def test_get(self):
        key = 'dqtest-{}'.format(uuid4())
        assert not Redis.get(key)
        Redis.setex(key, '1', 1)
        assert Redis.get(key) == '1'
        assert Redis.delete(key)
        assert not Redis.get(key)

    def test_get_json_string(self):
        key = 'dqtest-{}'.format(uuid4())
        assert not Redis.get(key)
        Redis.setex(key, [1, '2', True], 1)
        assert Redis.get(key) == '[1, "2", true]'
        Redis.setex(key, {'cornell': '#1'}, 1)
        assert Redis.get(key) == '{"cornell": "#1"}'

    def test_get_json(self):
        key = 'dqtest-{}'.format(uuid4())
        assert not Redis.get(key)
        Redis.setex(key, [1, '2', True], 1)
        assert Redis.get_json(key) == [1, '2', True]
        Redis.setex(key, {'cornell': '#1'}, 1)
        assert Redis.get_json(key) == {'cornell': '#1'}

    def test_expire(self):
        key = 'dqtest-{}'.format(uuid4())
        assert Redis.set(key, '1')
        assert Redis.expire(key, 1)
        sleep(1.5)
        assert not Redis.exists(key)

    def test_hash(self):
        key = 'dqtest-{}'.format(uuid4())
        assert not Redis.hgetall(key)
        assert not Redis.hget(key, '1')
        assert Redis.hset(key, '1', '1')
        assert Redis.hget(key, '1') == '1'
        assert Redis.hset(key, '2', '3')
        assert Redis.hget(key, '2') == '3'
        assert Redis.hset(key, '3', {'cornell': '#1'})
        assert Redis.hget(key, '3') == '{"cornell": "#1"}'
        assert Redis.hgetall(key) == {
            '1': '1', '2': '3', '3': '{"cornell": "#1"}'
        }
        assert Redis.hdelete(key, '1')
        assert Redis.hgetall(key) == {'2': '3', '3': '{"cornell": "#1"}'}
        assert Redis.delete(key)
        assert not Redis.exists(key)

    def test_list(self):
        key = 'dqtest-{}'.format(uuid4())
        assert not Redis.lpeek(key, 1)
        assert not Redis.lpop(key, 1)
        assert Redis.rpush(key, 1, 2)
        assert Redis.rpush(key, '3', [1, 2])
        assert Redis.lpeek(key, 1) == ['1']
        assert Redis.lpeek(key, 2) == ['1', '2']
        assert Redis.lpop(key, 2) == ['1', '2']
        assert Redis.lpop(key, 3) == ['3', '[1, 2]']
        assert not Redis.exists(key)

    def test_atomic_rw(self):
        def evaluator(x):
            return x + '#1'

        Redis.set('dqtest-rw', 'cornell ')
        success, no_error = Redis.atomic_rw('dqtest-rw', evaluator)
        assert success and no_error
        assert Redis.get('dqtest-rw') == 'cornell #1'
        Redis.delete('dqtest-rw')

    def test_atomic_rw_user_abort(self):
        def evaluator(x):
            return None

        Redis.set('dqtest-rw', 'meow')
        success, no_error = Redis.atomic_rw('dqtest-rw', evaluator)
        assert not success and no_error
        assert Redis.get('dqtest-rw') == 'meow'
        Redis.delete('dqtest-rw')

    def test_atomic_rw_error(self):
        def change():
            Redis.set('dqtest-rw', 'cornell')

        def evaluator(x):
            t = threading.Thread(target=change)
            t.start()
            sleep(0.5)
            return x + '#1'

        Redis.set('dqtest-rw', 'meow')
        success, no_error = Redis.atomic_rw('dqtest-rw', evaluator)
        assert not success and not no_error
        assert Redis.get('dqtest-rw') == 'cornell'
        Redis.delete('dqtest-rw')

    def test_atomic_rw_hash(self):
        def evaluator(x):
            return x + '#1'

        Redis.hset('dqtest-rwh', 'key', 'cornell ')
        succ, no_error = Redis.atomic_rw_hash('dqtest-rwh', 'key', evaluator)
        assert succ and no_error
        assert Redis.hget('dqtest-rwh', 'key') == 'cornell #1'
        Redis.delete('dqtest-rwh')

    def test_atomic_rw_hash_user_abort(self):
        def evaluator(x):
            return None

        Redis.hset('dqtest-rwh', 'key', 'meow')
        succ, no_error = Redis.atomic_rw_hash('dqtest-rwh', 'key', evaluator)
        assert not succ and no_error
        assert Redis.hget('dqtest-rwh', 'key') == 'meow'
        Redis.delete('dqtest-rwh')

    def test_atomic_rw_hash_error(self):
        def change():
            Redis.hset('dqtest-rwh', 'key', 'meow2')

        def evaluator(x):
            t = threading.Thread(target=change)
            t.start()
            sleep(0.5)
            return x + '#1'

        Redis.hset('dqtest-rwh', 'key', 'meow')
        succ, no_error = Redis.atomic_rw_hash('dqtest-rwh', 'key', evaluator)
        assert not succ and not no_error
        assert Redis.hget('dqtest-rwh', 'key') == 'meow2'
        Redis.delete('dqtest-rwh')
