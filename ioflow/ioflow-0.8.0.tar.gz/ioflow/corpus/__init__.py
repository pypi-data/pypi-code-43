corpus_processor_mapping = {}


def registry_corpus_processor_class(data_source_scheme, corpus_processor_class):
    corpus_processor_mapping[data_source_scheme] = corpus_processor_class


def get_corpus_processor_class(data_source_scheme):
    return corpus_processor_mapping[data_source_scheme]


def get_corpus_processor(config):
    corpus_processor_class = get_corpus_processor_class(config.get('data_source_scheme', 'local'))
    return corpus_processor_class(config)


from ioflow.corpus_processor.raw_corpus_processor import RawCorpusProcessor
registry_corpus_processor_class('raw', RawCorpusProcessor)

from ioflow.corpus_processor.local_corpus_processor import LocalCorpusProcessor
registry_corpus_processor_class('local', LocalCorpusProcessor)

from ioflow.corpus_processor.http_corpus_processor import HttpCorpusProcessor
registry_corpus_processor_class('http', HttpCorpusProcessor)

from ioflow.corpus_processor.download_corpus_processor import DownloadCorpusProcessor
registry_corpus_processor_class('remote_file', DownloadCorpusProcessor)
