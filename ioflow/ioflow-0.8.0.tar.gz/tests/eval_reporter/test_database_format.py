import json

from ioflow.eval_reporter import DbRequestData

from tokenizer_tools.tagset.offset.sequence import Sequence
from tokenizer_tools.tagset.offset.span import Span


def test_DbRequestData():
    seq = Sequence("王小明在北京的清华大学读书。", id="abc")
    seq.span_set.append(Span(0, 3, 'PERSON', '王小明'))
    seq.span_set.append(Span(4, 6, 'GPE', '北京'))
    seq.span_set.append(Span(7, 11, 'ORG', '清华大学'))

    db_data = DbRequestData.from_offset_corpus(seq)
    result = json.dumps(db_data, ensure_ascii=False)

    expected = """{"_id": "abc", "text": "王小明在北京的清华大学读书。", "annotations": [{"labels_type": "slot", "entities": [{"start_index": 0, "slot_len": 3, "slot_type": "PERSON", "slot_value": "王小明"}, {"start_index": 4, "slot_len": 10, "slot_type": "GPE", "slot_value": "北京"}, {"start_index": 7, "slot_len": 18, "slot_type": "ORG", "slot_value": "清华大学"}]}]}"""

    assert result == expected
