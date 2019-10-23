import pytest

from dictdaora import DictDaora


def test_should_set_get_attribute():
    daora = DictDaora()
    daora.fake = 'fake'

    assert daora.fake == 'fake'


def test_should_set_attr():
    daora = DictDaora()
    daora.set('fake', 'faked_value')

    assert daora['fake'] == 'faked_value'


def test_should_unset_attr():
    daora = DictDaora()
    daora.set('fake', 'faked_value')
    daora.unset('fake')

    with pytest.raises(AttributeError) as exc_info:
        daora.fake

    assert exc_info.value.args == ('fake',)


def test_should_unset_attr_error():
    daora = DictDaora()
    daora.set('fake', 'faked_value')
    daora.unset('fake')

    with pytest.raises(AttributeError) as exc_info:
        daora.unset('fake')

    assert exc_info.value.args == ('fake',)
