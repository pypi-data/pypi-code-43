import os

import pandas as pd
import pytest

from azureml.studio.core.utils.column_selection import ColumnKind
import azureml.studio.common.error as error_setting
from azureml.studio.common.datatable.data_table import DataTableColumnSelectionBuilder
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.modules.ml.tests.mltest_utils import assert_data_table_equals
from azureml.studio.modules.text_analytics.extract_ngram_feature_from_text.extract_ngram_features_from_text_module \
    import ExtractNGramFeaturesFromTextModule
from azureml.studio.modules.text_analytics.extract_ngram_feature_from_text.ngram_utils import VocabularyMode, \
    WeightingFunction, ReduceDimensionalityMode, ScoringMethod, VocabDataSetColumnName, NGramFeaturesConstants


def script_directory():
    return os.path.dirname(os.path.abspath(__file__))


def _base_library():
    return os.path.join(script_directory(), 'input')


def _feature_ref_file_name():
    return 'feature_ref.tsv'


def _vocab_ref_file_name():
    return 'vocab_ref.tsv'


def _input_vocab_name():
    return 'input_vocab.tsv'


@pytest.fixture
def entry_params():
    params_dict = {
        'detect_oov': False,
        'vocabulary_mode': VocabularyMode.Create,
        'ngrams_size': 2,
        'k_skip_size': 0,
        'weighting_func': WeightingFunction.WeightTf,
        'min_word_length': 3,
        'max_word_length': 25,
        'min_doc_freq': 2.0,
        'max_doc_freq': 1.0,
        'include_sentence_prefix': False,
        'normalize_feature_vector': True,
        'reduce_dimensionality': ReduceDimensionalityMode.FALSE,
        'method': ScoringMethod.CountBased,
        'target_column_index_or_name': None,
        'feature_count': 1,
        'threshold': 3
    }
    return params_dict


@pytest.fixture
def simple_data():
    return DataTable(pd.DataFrame({'label': [1, 0],
                                   'text': ["Let's catch pokemon like blastoise and mew two",
                                            "Have you caught any rare pokemon outside today?"]
                                   }))


@pytest.fixture
def simple_vocab():
    return DataTable(pd.DataFrame([{'Id': 1, 'NGram': 'thai', 'DF': 5, 'IDF': 5.568},
                                   {'Id': -1, 'NGram': NGramFeaturesConstants.NumberOfDocuments, 'DF': 5, 'IDF': 0}]))


@pytest.fixture
def create_mode_input_dataset():
    return DataTable(pd.read_csv(os.path.join(_base_library(), 'split_dataset_1.tsv'), sep='\t'))


@pytest.fixture
def read_only_mode_input_dataset():
    return DataTable(pd.read_csv(os.path.join(_base_library(), 'split_dataset_2.tsv'), sep='\t'))


# Invalid Input Dataset Region
def test_empty_dataset(entry_params):
    cs = DataTableColumnSelectionBuilder().include_all().build()
    with pytest.raises(error_setting.TooFewRowsInDatasetError,
                       match=f'Number of rows in input dataset "Dataset" is 0, less than allowed '):
        ExtractNGramFeaturesFromTextModule.run(input_dataset=DataTable(), text_column_index_or_name=cs,
                                               vocab_dataset=None,
                                               **entry_params)


def test_no_text_column_selected(entry_params, simple_data):
    cs = DataTableColumnSelectionBuilder().include_col_kinds(ColumnKind.LABEL).build()
    with pytest.raises(error_setting.NoColumnsSelectedError,
                       match='Specified column set "Text column" does not apply to any of dataset columns.'):
        ExtractNGramFeaturesFromTextModule.run(input_dataset=simple_data, text_column_index_or_name=cs,
                                               vocab_dataset=None, **entry_params)


def test_more_than_one_column_selected(entry_params, simple_data):
    cs = DataTableColumnSelectionBuilder().include_all().build()
    with pytest.raises(error_setting.BadNumberOfSelectedColumnsError,
                       match='Column selection pattern "Text column" is'):
        ExtractNGramFeaturesFromTextModule.run(input_dataset=simple_data, text_column_index_or_name=cs,
                                               vocab_dataset=None, **entry_params)


def test_not_string_column_selected(entry_params, simple_data):
    cs = DataTableColumnSelectionBuilder().include_col_names('label').build()
    with pytest.raises(error_setting.InvalidColumnTypeError,
                       match='Cannot process column "label" of type int64.'):
        ExtractNGramFeaturesFromTextModule.run(input_dataset=simple_data, text_column_index_or_name=cs,
                                               vocab_dataset=None, **entry_params)


# Invalid Vocabulary Region

@pytest.mark.parametrize('vocab_mode', [
    VocabularyMode.ReadOnly,
    VocabularyMode.Merge,
    VocabularyMode.Update,
])
def test_missing_vocab(vocab_mode, entry_params, simple_data):
    cs = DataTableColumnSelectionBuilder().include_col_names('text').build()
    entry_params['vocabulary_mode'] = vocab_mode
    with pytest.raises(error_setting.TooFewRowsInDatasetError,
                       match=f'Number of rows in input dataset "Input vocabulary" is 0, less than allowed '):
        ExtractNGramFeaturesFromTextModule.run(input_dataset=simple_data, text_column_index_or_name=cs,
                                               vocab_dataset=DataTable(), **entry_params)


@pytest.mark.parametrize('drop_name', [
    VocabDataSetColumnName.NGramID,
    VocabDataSetColumnName.NGramString,
    VocabDataSetColumnName.DocumentFrequency,
    VocabDataSetColumnName.InverseDocumentFrequency
])
def test_vocab_missing_column(drop_name, entry_params, simple_data, simple_vocab: DataTable):
    cs = DataTableColumnSelectionBuilder().include_col_names('text').build()
    entry_params['vocabulary_mode'] = VocabularyMode.ReadOnly
    simple_vocab.rename_column(drop_name, 'new_name')
    with pytest.raises(error_setting.ColumnNotFoundError,
                       match=f'Column with name or index "{drop_name}" does not exist '):
        ExtractNGramFeaturesFromTextModule.run(input_dataset=simple_data, text_column_index_or_name=cs,
                                               vocab_dataset=simple_vocab, **entry_params)


def test_create_empty_vocab(entry_params, simple_data):
    entry_params['min_doc_freq'] = 5.0
    cs = DataTableColumnSelectionBuilder().include_col_names('text').build()
    with pytest.raises(error_setting.FailedToCompleteOperationError, match="The vocabulary is empty."):
        ExtractNGramFeaturesFromTextModule.run(input_dataset=simple_data, text_column_index_or_name=cs, **entry_params)


@pytest.mark.parametrize("vocab_mode", [VocabularyMode.Create, VocabularyMode.ReadOnly])
@pytest.mark.parametrize("weight_function",
                         [WeightingFunction.WeightBin, WeightingFunction.WeightIdf, WeightingFunction.WeightTf,
                          WeightingFunction.WeightTFIDF]
                         )
def test_processing_missing_value(vocab_mode, weight_function, entry_params, simple_vocab):
    import numpy as np
    entry_params['min_doc_freq'] = 1.0
    entry_params['vocabulary_mode'] = vocab_mode
    entry_params['weighting_func'] = weight_function
    cs = DataTableColumnSelectionBuilder().include_col_names('text').build()
    test_df = pd.DataFrame({'text': ["hello world .", None, np.nan, "Let's catch pokemon like blastoise and mew two"]})
    ExtractNGramFeaturesFromTextModule.run(input_dataset=DataTable(test_df), text_column_index_or_name=cs,
                                           vocab_dataset=simple_vocab, **entry_params)


# Correctness Test Region
# test the result under create vocabulary mode is consistent with v1.
@pytest.mark.parametrize('weight_function, ref_path', [
    (WeightingFunction.WeightTf, os.path.join(_base_library(), 'create_tf')),
    (WeightingFunction.WeightTFIDF, os.path.join(_base_library(), 'create_tf_idf')),
    (WeightingFunction.WeightIdf, os.path.join(_base_library(), 'create_idf')),
    (WeightingFunction.WeightBin, os.path.join(_base_library(), 'create_bin'))
])
def test_create_vocab_correctness(weight_function, ref_path, create_mode_input_dataset, entry_params):
    ref_feature = DataTable(pd.read_csv(os.path.join(ref_path, _feature_ref_file_name()), sep='\t'))
    ref_vocab = DataTable(pd.read_csv(os.path.join(ref_path, _vocab_ref_file_name()), sep='\t'))
    cs = DataTableColumnSelectionBuilder().include_col_names('Col2').build()
    entry_params['vocabulary_mode'] = VocabularyMode.Create
    entry_params['weighting_func'] = weight_function
    entry_params['ngrams_size'] = 3
    entry_params['max_doc_freq'] = 0.5
    out_feature, out_vocab = ExtractNGramFeaturesFromTextModule.run(input_dataset=create_mode_input_dataset,
                                                                    text_column_index_or_name=cs, **entry_params)
    df = ref_feature.data_frame.drop(columns='NGramsString')

    ref_feature = DataTable(df)  # DataTable(ref_feature.data_frame.drop(columns='NGramsString'))
    assert_data_table_equals(ref_vocab, out_vocab)
    assert_data_table_equals(ref_feature, out_feature)


# test the result under read only vocabulary mode is consistent with v1.
@pytest.mark.parametrize('weight_function, ref_path', [
    (WeightingFunction.WeightTf, os.path.join(_base_library(), 'read_tf')),
    (WeightingFunction.WeightTFIDF, os.path.join(_base_library(), 'read_tf_idf')),
    (WeightingFunction.WeightIdf, os.path.join(_base_library(), 'read_idf')),
    (WeightingFunction.WeightBin, os.path.join(_base_library(), 'read_bin'))
])
def test_read_vocab_correctness(weight_function, ref_path, read_only_mode_input_dataset, entry_params):
    input_vocab = DataTable(pd.read_csv(os.path.join(ref_path, _input_vocab_name()), sep='\t'))
    ref_feature = DataTable(pd.read_csv(os.path.join(ref_path, _feature_ref_file_name()), sep='\t'))
    ref_vocab = DataTable(pd.read_csv(os.path.join(ref_path, _vocab_ref_file_name()), sep='\t'))
    cs = DataTableColumnSelectionBuilder().include_col_names('Col2').build()
    entry_params['vocabulary_mode'] = VocabularyMode.ReadOnly
    entry_params['weighting_func'] = weight_function
    entry_params['ngrams_size'] = 3
    entry_params['max_doc_freq'] = 0.5
    out_feature, out_vocab = ExtractNGramFeaturesFromTextModule.run(input_dataset=read_only_mode_input_dataset,
                                                                    vocab_dataset=input_vocab,
                                                                    text_column_index_or_name=cs, **entry_params)
    df = ref_feature.data_frame.drop(columns='NGramsString')
    ref_feature = DataTable(df)
    assert_data_table_equals(ref_vocab, out_vocab)
    assert_data_table_equals(ref_feature, out_feature)
