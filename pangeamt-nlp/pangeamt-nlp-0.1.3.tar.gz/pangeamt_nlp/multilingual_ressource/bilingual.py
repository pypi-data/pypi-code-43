from typing import Optional, Tuple



class Bilingual:
    def __init__(self, src_file: str, tgt_file: str, src_file_encoding: Optional[str] = None,
                 tgt_file_encoding: Optional[str] = None):
        self._src_file = src_file
        self._tgt_file = tgt_file
        self._src_file_encoding = src_file_encoding
        self._tgt_file_encoding = tgt_file_encoding

    def analyze(self):
        # Todo count
        pass

    def read(self, reader=None) -> Tuple[str, str]:
        with open(self._src_file, 'r', encoding=self._src_file_encoding) as src_file:
            with open(self._tgt_file, 'r', encoding=self._tgt_file_encoding) as tgt_file:
                num_line = 0
                while True:
                    src = src_file.readline()
                    tgt = tgt_file.readline()

                    if src == '' or tgt == '':
                        if src != '' or tgt != '':
                            raise ValueError(
                                f'Bilingual files "{self._src_file}" and "{self._tgt_file}" do not have the same number of lines')
                        else:
                            return

                    if src.strip() == '':
                        raise ValueError(f'Bilingual file "{self._src_file}" has an empty line at line {num_line}')

                    if tgt.strip() == '':
                        raise ValueError(f'Bilingual file "{self._tgt_file}" has an empty line at line {num_line}')

                    num_line += 1
                    yield src, tgt



