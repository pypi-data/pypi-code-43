from typing import List
from pangeamt_nlp.processor.base.transformer_base import TransformerBase
from pangeamt_nlp.seg import Seg


class PipelineDecoding:
    def __init__(self, processors: List[TransformerBase]):
        self._processors = processors
        self._inverted_processors = reversed(processors)

    def process_src(self, seg: Seg):
        for p in self._processors:
            p.process_src_decoding(seg)

    def process_tgt(self, seg: Seg):
        for p in self._inverted_processors:
            p.process_tgt_decoding(seg)
