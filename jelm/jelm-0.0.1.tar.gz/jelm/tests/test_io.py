import json

from jelm import read_json_dump, Jelm


def test_json_dump_read():

    test_dic = {
        'metadata': {'author': 'me'},
        'objects': []
    }

    dump = json.dumps(test_dic)

    jelm = read_json_dump(dump)

    assert isinstance(jelm, Jelm)
