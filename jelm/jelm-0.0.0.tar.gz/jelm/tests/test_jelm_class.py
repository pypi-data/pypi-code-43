import pytest

from jelm import Jelm


def test_init():

    jelm = Jelm(metadata={'author': 'John Doe'},
                objects=[])

    with pytest.raises(ValueError):
        jelm2 = Jelm(bad_kwarg="fing")

    assert isinstance(jelm.objects, list)
    assert isinstance(jelm.metadata, dict)


def test_get():

    jelm = Jelm()

    assert isinstance(jelm.get_dict(), dict)
    assert isinstance(jelm.get_json(), str)


def test_add_object():

    jelm = Jelm()

    jelm.add_object({'type': 'edge',
                     'source': 'n1',
                     'target': 'n2'})

    jelm.add_object({'type': 'node',
                     'id': 'n1'})

    from jelm.core.jelm_class import Node

    jelm.add_object(Node(id='n2'))

    jelm.add_object(Node(id='n3',
                         attributes={'priority': 'low'}))

    with pytest.raises(ValueError):
        jelm.add_object({'no': 'type'})

    with pytest.raises(ValueError):
        jelm.add_object({'type': 'wrong'})
