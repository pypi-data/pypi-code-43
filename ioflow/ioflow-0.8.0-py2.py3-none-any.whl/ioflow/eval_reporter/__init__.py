import json
import os
import tempfile
import zipfile

import jsonlines
import requests

from tokenizer_tools.tagset.offset.sequence import Sequence


class DbRequestData(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self['_id'] = None
        self['text'] = None
        self['annotations'] = []

    @classmethod
    def from_offset_corpus(cls, offset_corpus: Sequence):
        self_instance = cls()

        # Notice: id of a Sequence object maybe is a UUID object,
        # hence need use str() convert string
        self_instance['_id'] = str(offset_corpus.id)
        self_instance['text'] = "".join(offset_corpus.text)
        self_instance['annotations'] = []

        entities = []
        for span in offset_corpus.span_set:
            entity = {
                'start_index': span.start,
                'slot_len': span.start + span.end,
                'slot_type': span.entity,
                'slot_value': span.value
            }

            entities.append(entity)

        self_instance['annotations'] = [
            {
                "labels_type": "slot",
                "entities": entities
            }
        ]

        return self_instance


eval_reporter_mapping = {}


def registry_eval_reporter_class(data_source_scheme, corpus_processor_class):
    eval_reporter_mapping[data_source_scheme] = corpus_processor_class


def get_eval_reporter_class(config):
    return eval_reporter_mapping[config.get('eval_reporter_scheme', 'local')]


def get_eval_reporter(config) -> 'BaseEvalReporter':
    eval_reporter_class = get_eval_reporter_class(config)
    return eval_reporter_class(config)


class BaseEvalReporter:
    def __init__(self, config):
        self.config = config

    def record_x_and_y(self, x, y):
        raise NotImplementedError

    def submit(self):
        raise NotImplementedError


class LocalEvalReporter(BaseEvalReporter):
    def record_x_and_y(self, x, y):
        print("<{}>:\n\tx:{};\n\ty:{}".format(self.__class__, x, y))

    def submit(self):
        pass


class RemoteFileEvalReporter(BaseEvalReporter):
    def __init__(self, config):
        super().__init__(config)

        self.x_list = []
        self.y_list = []

    def record_x_and_y(self, x, y):
        if isinstance(x, Sequence):
            x = DbRequestData.from_offset_corpus(x)

        self.x_list.append(x)
        self.y_list.append(y)

    @staticmethod
    def _write_json_lines(file_, data_list):
        with jsonlines.open(file_, mode='w') as writer:
            for x in data_list:
                writer.write(x)

    @staticmethod
    def _write_zip_file(zip_file, file_list):
        with zipfile.ZipFile(zip_file, 'w') as fd:
            for file_ in file_list:
                fd.write(file_, os.path.basename(file_))

    def submit(self):
        work_dir = tempfile.mkdtemp()

        x_file = os.path.join(work_dir, 'x.jsonl')
        self._write_json_lines(x_file, self.x_list)

        y_file = os.path.join(work_dir, 'y.jsonl')
        self._write_json_lines(y_file, self.y_list)

        x_zip_file = os.path.join(work_dir, 'x.jsonl.zip')
        self._write_zip_file(x_zip_file, [x_file])

        y_zip_file = os.path.join(work_dir, 'y.jsonl.zip')
        self._write_zip_file(y_zip_file, [y_file])

        files = [
            ('multipartFiles', ('x.jsonl.zip', open(x_zip_file, 'rb'), 'application/zip', {'Expires': '0'})),
            ('multipartFiles', ('y.jsonl.zip', open(y_zip_file, 'rb'), 'application/zip', {'Expires': '0'}))
        ]

        r = requests.post(self.config['eval_reporter_url'],
                          data={'id': self.config['task_id']},
                          files=files)

        assert r.ok, r.content


registry_eval_reporter_class('local', LocalEvalReporter)
registry_eval_reporter_class('http', RemoteFileEvalReporter)
