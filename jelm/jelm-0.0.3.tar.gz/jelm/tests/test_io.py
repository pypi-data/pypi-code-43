import json
import os

from jelm.core.jelm_class import Jelm
from jelm.core.io import reads_json, read_json


def test_json_reads():

    test_dic = {
        'metadata': {'author': 'me'},
        'objects': []
    }

    dump = json.dumps(test_dic)

    jelm = reads_json(dump)

    assert isinstance(jelm, Jelm)


def test_json_read(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "fing.jelm"

    test_dic = {
        'metadata': {'author': 'me'},
        'objects': []
    }

    dump = json.dumps(test_dic)

    p.write_text(dump)

    fp = os.fspath(p)

    el = read_json(fp)

    assert isinstance(el, Jelm)
