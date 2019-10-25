import json
from pangeamt_nlp.utils.raise_exception_if_file_not_found import raise_exception_if_file_not_found
from pangeamt_nlp.utils.raise_exception_if_file_found import raise_exception_if_file_found
from pangeamt_nlp.multilingual_ressource.af.af_header import AfHeader


class Af:
    SEP = '|||'
    HEADER_SEP = '###\n'

    def __init__(self, file):
        raise_exception_if_file_not_found(file)
        self._file = file
        self._header = AfHeader.create_from_json(Af.read_header(file))
        self._num_trans_units = None
        self._writer = AfWriter(self._file)

    @staticmethod
    def new(file, left_lang=None,
            left_translator=None,
            left_translation_type=None,
            right_lang=None,
            right_translator=None,
            right_translation_type=None,
            corpus_file=None,
            corpus_name=None,
            corpus_domain=None):

        raise_exception_if_file_found(file)

        with open(file, 'w', encoding='utf-8') as f:
            header = AfHeader(left_lang,
                              left_translator,
                              left_translation_type,
                              right_lang,
                              right_translator,
                              right_translation_type,
                              corpus_file,
                              corpus_name,
                              corpus_domain)
            f.write(header.to_string())
        return Af(file)

    def read(self, reader=None):
        if reader is not None:
            reader.initialize(self)
        header_sep_found = False
        with open(self._file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if not header_sep_found:
                    if line == Af.HEADER_SEP:
                        header_sep_found = True
                    continue
                line = line.strip()
                parts = line.split(self.SEP)
                try:
                    left = parts[1]
                    right = parts[2]
                except:
                    raise ValueError(f"Invalid line `{i+1}`")
                if reader:
                    yield reader.read(left, right)
                else:
                    yield left, right

    @staticmethod
    def read_header(file: str):
        header = ''
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                if line != Af.HEADER_SEP:
                    header += line
                else:
                    return json.loads(header)
            raise HeaderSepNotFoundException(file)

    def get_header(self):
        return self._header

    header = property(get_header)

    def get_file(self):
        return self._file

    file = property(get_file)

    def get_num_trans_units(self):
        if self._num_trans_units is None:
            header_sep_found = False
            num = 0
            with open(self._file, 'rb') as f:
                for line in f:
                    if not header_sep_found:
                        line = line.decode('utf-8')
                        if line == Af.HEADER_SEP:
                            header_sep_found = True
                        continue
                    num += 1
            return num
        return self._num_trans_units

    num_trans_units = property(get_num_trans_units)

    def get_writer(self):
        return self._writer

    writer = property(get_writer)


class HeaderSepNotFoundException:
    def __init__(self, file: str):
        super().__init__(f'Af header sep `{Af.SEP.strip()}`not found in {file} ')


class AfWriter:
    def __init__(self, file: str):
        self._file = file
        self._file_handler = None

    def __enter__(self):
        self._file_handler = open(self._file, 'a', encoding='utf-8')
        return self

    def __exit__(self, type, value, tb):
        self._file_handler.close()
        self._file_handler = None

    def write(self, id, left, right):
        self._file_handler.write(str(id) + Af.SEP + left + Af.SEP + right + '\n')

    def write_raw(self, line):
        self._file_handler.write(line)
