import io

from ioflow.corpus_processor.download_corpus_processor import (
    parse_std_corpus_to_offset,
    generator_fn,
    parse_corpus_to_offset)


def test_parse_std_corpus_to_offset():
    test_input = {
        "id": "5d11c0344420bb1e20078fd9",
        "annotations": {
            "entity": [
                {
                    "start": "0",
                    "length": "3",
                    "type": "人名"
                },
                {
                    "start": "4",
                    "length": "3",
                    "type": "歌曲"
                }
            ]
        },
        "text": "周杰伦的七里香",
        "classifications": {
            "intent": "PLAY_SONG",
            "domain": "yyy"
        }
    }

    result = parse_std_corpus_to_offset(test_input)

    gold_result_str = "Sequence(text='周杰伦的七里香', span_set=SpanSet([Span(0, 3, '人名', value='周杰伦', normal_value=None), Span(4, 7, '歌曲', value='七里香', normal_value=None)]), id='5d11c0344420bb1e20078fd9', label='PLAY_SONG', extra_attr={})"

    assert str(result) == gold_result_str


def test_parse_corpus_to_offset():
    # TODO(howl-anderson): disable this test case
    return None

    test_input = {
        "_id": "5cff6f124f43a05bf437c09c",
        "text_id": "ae1188f49ef4d855183aa60ce4d9b5fa",
        "editor": "quanlin",
        "time_stamp": "2019-06-11 16:47:40",
        "annotations": [
            {
                "labels_type": "slot",
                "time_stamp": "2019-06-11 16:48:04",
                "slot_num": 1,
                "entities": [
                    {
                        "start_index": 8,
                        "slot_len": 2,
                        "slot_type": "唤醒词名",
                        "slot_value": "大白"
                    }
                ],
                "label_name": "slot",
                "label_id": "5ceb6a314420bb3e18596e58",
                "is_delete": False
            }
        ],
        "text": "改个唤醒词",
        "is_delete": False,
        "name": "collection1",
        "label_id": "5ceb6a314420bb3e18596e57"
    }

    result = parse_corpus_to_offset(test_input)

    gold_result_str = "Sequence(text='周杰伦的七里香', span_set=SpanSet([Span(0, 3, '人名', value='周杰伦', normal_value=None), Span(4, 7, '歌曲', value='七里香', normal_value=None)]), id='5d11c0344420bb1e20078fd9', label='PLAY_SONG')"

    assert str(result) == gold_result_str


def test_generator_fn(mocker):
    gold_result = ['a', 'b', 'c']

    # mock open() learned from https://gist.github.com/ViktorovEugene/27d76ad2d94c88170d7b
    mocked_open = mocker.patch('builtins.open')
    mocked_open.return_value = io.StringIO('\n'.join(gold_result))

    mocked_json_loads = mocker.patch('json.loads')
    mocked_json_loads.side_effect = lambda x: x.strip()

    mocked_parse_corpus_to_offset = mocker.patch('ioflow.corpus_processor.download_corpus_processor.parse_corpus_to_offset')
    mocked_parse_corpus_to_offset.side_effect = lambda x: x

    result = generator_fn(None)

    assert list(result) == gold_result

