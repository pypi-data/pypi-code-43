from uuid import uuid4

from pytest import fixture, raises

from persistentdict.dict_in_redis import PersistentDict


class TestPersistentDict:
    @fixture
    def db(self):
        return PersistentDict(hash_name=str(uuid4()))

    @fixture
    def dictionary(self):
        return {
            "key": "some value",
            "key2": ["an", "array"],
            "key3": {"a": "dictionary", "b": 2, "c": ["one"]},
        }

    def test_one_by_one(self, db, dictionary):
        for key, value in dictionary.items():
            assert key not in db
            db[key] = value
            assert key in db
            assert db[key] == value
            del db[key]
            assert key not in db

    def test_more_keys(self, db, dictionary):
        assert len(db) == 0
        for key, value in dictionary.items():
            assert key not in db
            db[key] = value
        assert len(db) == len(dictionary)
        assert len(db.get_all()) == len(dictionary)
        assert db.get_all() == dictionary
        assert len(db.items()) == len(dictionary)
        assert db.keys() == dictionary.keys()
        db.clear()
        assert len(db) == 0

    def test_should_raise_key_error_if_key_is_not_in_db(self, db, dictionary):
        with raises(KeyError, match="Key 'unknown' does not exist."):
            db['unknown']
    
    def test_should_get_none_if_no_default(self, db, dictionary):
        actual = db.get('unknown')
        assert actual is None
    
    def test_should_get_default_if_no_key(self, db, dictionary):
        actual = db.get('unknown', 'default')
        assert actual == 'default'
    
    def test_should_get_value(self, db, dictionary):
        db['key'] = 'value'
        actual = db.get('key')
        assert actual == 'value'
