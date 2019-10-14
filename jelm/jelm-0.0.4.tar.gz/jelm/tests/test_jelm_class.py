import pytest

from jelm import Jelm, Node, Edge


def test_init():

    el = Jelm(metadata={'author': 'John Doe'},
              objects=[])

    with pytest.raises(ValueError):
        el2 = Jelm(bad_kwarg="fing")

    assert isinstance(el.objects, list)
    assert isinstance(el.metadata, dict)


def test_add_object():

    el = Jelm()

    el.add_object({'type': 'edge',
                   'source': 'n1',
                   'target': 'n2'})

    el.add_object({'type': 'node',
                   'id': 'n1'})

    el.add_object(Node(id='n2'))

    el.add_object(Node(id='n3',
                       attributes={'priority': 'low'}))

    with pytest.raises(ValueError):
        el.add_object({'no': 'type'})

    with pytest.raises(ValueError):
        el.add_object({'type': 'wrong'})

    el.add_edge('n3', 'n2')

    el.add_node('n4', {'order': 'latest'})

    assert len(set([o['type'] for o in el.objects])) > 1
    assert el.objects[0]['type'] == 'edge'
    assert el.objects[1]['type'] == 'node'


def test_iter():

    el = Jelm(metadata={'author': 'John Doe'},
              objects=[{'type': 'node',
                        'id': 'n1'},
                       {'type': 'node',
                        'id': 'n2'},
                       {'type': 'edge',
                        'source': 'n1',
                        'target': 'n2'}]
              )

    for idx, o in enumerate(el):
        if idx < 2:
            assert isinstance(o, Node)
        else:
            assert isinstance(o, Edge)
