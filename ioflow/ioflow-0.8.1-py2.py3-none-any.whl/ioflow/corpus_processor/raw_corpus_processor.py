from ioflow.corpus_processor.corpus_processor_base import CorpusProcessorBase


class RawCorpusProcessor(CorpusProcessorBase):
    def __init__(self, config):
        super(RawCorpusProcessor, self).__init__(config)
        self.dataset_mapping = {}

    def prepare(self):
        self.dataset_mapping[self.TRAIN] = self.config[
            'corpus_train_input_func']
        self.dataset_mapping[self.EVAL] = self.config[
            'corpus_eval_input_func']

        self.meta_info = self.config['corpus_meta_info']
