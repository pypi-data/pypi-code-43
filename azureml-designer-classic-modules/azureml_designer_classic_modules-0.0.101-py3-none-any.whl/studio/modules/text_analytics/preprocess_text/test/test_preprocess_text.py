import pytest
import os
import pandas as pd
import numpy as np
import azureml.studio.common.error as error_setting
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.datatable.data_table import DataTableColumnSelectionBuilder
from ..preprocess_text import PreprocessTextModule, PreprocessTextTrueFalseType, PreprocessTextLanguage
from ..preprocess_text_utils import PreprocessTextConstant

TargetColumnName = "text"
StopwordsColumnName = "stopwords"


def preprocess_text_params_negative():
    preprocess_text_params = {'language': PreprocessTextLanguage.English,
                              'language_column': None,
                              'text_column': DataTableColumnSelectionBuilder().include_all().build(),
                              'remove_stopwords': False,
                              'use_lemmatization': False,
                              'part_of_speech_filter': PreprocessTextTrueFalseType.FALSE,
                              'filter_nouns': False,
                              'filter_adjectives': False,
                              'filter_verbs': False,
                              'detect_sentences': False,
                              'normalize_case': False,
                              'remove_numbers': False,
                              'remove_special_characters': False,
                              'remove_duplicate_characters': False,
                              'remove_emails': False,
                              'remove_urls': False,
                              'expand_verb_contractions': False,
                              'normalize_slashes': False,
                              'split_tokens_by_chars': False,
                              'custom_expression': None,
                              'custom_replacement': None}
    return preprocess_text_params


def preprocess_text_params_positive():
    preprocess_text_params = {'language': PreprocessTextLanguage.English,
                              'language_column': None,
                              'text_column': DataTableColumnSelectionBuilder().include_all().build(),
                              'remove_stopwords': True,
                              'use_lemmatization': True,
                              'part_of_speech_filter': PreprocessTextTrueFalseType.FALSE,
                              'filter_nouns': False,
                              'filter_adjectives': False,
                              'filter_verbs': False,
                              'detect_sentences': True,
                              'normalize_case': True,
                              'remove_numbers': True,
                              'remove_special_characters': True,
                              'remove_duplicate_characters': True,
                              'remove_emails': True,
                              'remove_urls': True,
                              'expand_verb_contractions': True,
                              'normalize_slashes': True,
                              'split_tokens_by_chars': True,
                              'custom_expression': None,
                              'custom_replacement': None}
    return preprocess_text_params


def _gen_english_smoke_test():
    documents = [["What a beautiful day outside, let's go and play Pokemon Go!  Gotta catch em all!"]]
    stopwords = None
    params = preprocess_text_params_positive()
    output_ref = [["beautiful day outside let play pokemon go ||| got catch em"]]
    return documents, stopwords, params, output_ref


def _gen_remove_stopwords():
    documents = [["Python is an interpreted, high-level, general-purpose programming language."]]
    stopwords = [['language'], ['Python']]
    params = preprocess_text_params_negative()
    params['remove_stopwords'] = True
    output_ref = [["is an interpreted , high - level , general - purpose programming ."]]

    return documents, stopwords, params, output_ref


def _gen_detect_sentences():
    documents = [["Addition, subtraction, and multiplication are the same, but the "
                  "behavior of division differs. Due to concern about the amount of "
                  "code written for Python 2, support for Python 2.7 (the last "
                  "release in the 2.x series) was extended to 2020. Language developer"
                  " Guido van Rossum shouldered sole responsibility for the project "
                  "until July 2018 but now shares his leadership as a member of a "
                  "five-person steering council."]]
    stopwords = None
    params = preprocess_text_params_negative()
    params['detect_sentences'] = True
    output_ref = [["Addition , subtraction , and multiplication are the same , but the "
                   "behavior of division differs . ||| Due to concern about the amount of "
                   "code written for Python 2 , support for Python 2.7 ( the last release "
                   "in the 2.x series ) was extended to 2020 . ||| Language developer Guido "
                   "van Rossum shouldered sole responsibility for the project until July"
                   " 2018 but now shares his leadership as a member of a five - person "
                   "steering council ."]]
    return documents, stopwords, params, output_ref


def _gen_remove_numbers():
    documents = [["There are some numbers: 100, 2.5, 10e5, 6.x"]]
    stopwords = None
    params = preprocess_text_params_negative()
    params['remove_numbers'] = True
    output_ref = [["There are some numbers : , , ,"]]
    return documents, stopwords, params, output_ref


def _gen_remove_special_characters():
    documents = [["There are some special characters: $(#)@|?"]]
    stopwords = None
    params = preprocess_text_params_negative()
    params['remove_special_characters'] = True
    output_ref = [["There are some special characters"]]
    return documents, stopwords, params, output_ref


def _gen_remove_duplicate_characters():
    documents = [['aa'], ['aaa'], ['aaaa'], ['baaaaab']]
    stopwords = None
    params = preprocess_text_params_negative()
    params['remove_duplicate_characters'] = True
    output_ref = [['aa'], ['aa'], ['aa'], ['baab']]
    return documents, stopwords, params, output_ref


def _gen_remove_emails():
    documents = [['thisisemail@gamil.com'], ['thisisnotanemail@messycode'], ['thisisalsonotanemail@.com']]
    stopwords = None
    params = preprocess_text_params_negative()
    params['remove_emails'] = True
    output_ref = [[''], ['thisisnotanemail@messycode'], ['thisisalsonotanemail@.com']]
    return documents, stopwords, params, output_ref


def _gen_remove_urls():
    documents = [['valid url: https://en.wikipedia.org/wiki/Python_(programming_language)'],
                 ['valid url: ftp://user:password@host:port/path in the text']]
    stopwords = None
    params = preprocess_text_params_negative()
    params['remove_urls'] = True
    output_ref = [['valid url :'], ['valid url : in the text']]
    return documents, stopwords, params, output_ref


def _gen_expand_verb_contractions():
    documents = [["let's go to the park."],
                 ["I can't believe that."],
                 ["I wouldn't stay there."]]
    stopwords = None
    params = preprocess_text_params_negative()
    params['expand_verb_contractions'] = True
    output_ref = [['let us go to the park .'],
                  ['I can not believe that .'],
                  ['I would not stay there .']]
    return documents, stopwords, params, output_ref


def _gen_normalize_backslashes():
    documents = [["\\"], ["\\\\"]]
    stopwords = None
    params = preprocess_text_params_negative()
    params['normalize_slashes'] = True
    output_ref = [["/"], ["//"]]
    return documents, stopwords, params, output_ref


def _gen_split_tokens_by_chars():
    documents = [["PEP 483 -- The Theory of Type Hints"], ["MS---WORD"]]
    stopwords = None
    params = preprocess_text_params_negative()
    params['split_tokens_by_chars'] = True
    output_ref = [["PEP 483 -- The Theory of Type Hints"], ["MS - WORD"]]
    return documents, stopwords, params, output_ref


def _gen_non_null_custom_expression():
    documents = [["There are many pokemon out there to catch today"],
                 ["The strongest pokemon in the world are waiting for you"],
                 ["Markizyabrishe is a \"pokemon\" who has the special ability to sleep all day and meow"]]
    stopwords = None
    params = preprocess_text_params_negative()
    params['custom_expression'] = "pokemon"
    params['custom_replacement'] = "fluffy"
    output_ref = [["There are many fluffy out there to catch today"],
                  ["The strongest fluffy in the world are waiting for you"],
                  ["Markizyabrishe is a \" fluffy \" who has the special ability to sleep all day and meow"]]
    return documents, stopwords, params, output_ref


def _gen_null_custom_expression():
    documents = [["There are many pokemon out there to catch today"],
                 ["The strongest pokemon in the world are waiting for you"],
                 ["Markizyabrishe is a \"pokemon\" who has the special ability to sleep all day and meow"]]
    stopwords = None
    params = preprocess_text_params_negative()
    params['custom_expression'] = "pokemon"
    output_ref = [["There are many out there to catch today"],
                  ["The strongest in the world are waiting for you"],
                  ["Markizyabrishe is a \" \" who has the special ability to sleep all day and meow"]]
    return documents, stopwords, params, output_ref


def _gen_missing_input_dataset():
    documents = [["Blue..."], [None], ["，，，Green"], [np.nan]]
    stopwords = None
    params = preprocess_text_params_positive()
    output_ref = [["blue"], [None], ["green"], [np.nan]]
    return documents, stopwords, params, output_ref


def _gen_mix_type_dataset():
    documents = [["text"], [2], [3.5]]
    stopwords = None
    params = preprocess_text_params_negative()
    output_ref = [["text"], [2], [3.5]]
    return documents, stopwords, params, output_ref


def _gen_null_dataset():
    dataset = None
    stopwords = None
    params = preprocess_text_params_positive()
    error = error_setting.NullOrEmptyError
    msg = "Input \"Dataset\" is null or empty."
    return dataset, stopwords, params, error, msg


def _gen_zero_row_dataset():
    dataset = DataTable(pd.DataFrame({TargetColumnName: []}))
    stopwords = None
    params = preprocess_text_params_positive()
    error = error_setting.TooFewRowsInDatasetError
    msg = r"Number of rows in input dataset \"Dataset\" is 0, less " \
          r"than allowed minimum of 1 row\(s\)."
    return dataset, stopwords, params, error, msg


def _gen_empty_dataset():
    dataset = DataTable(pd.DataFrame({}))
    stopwords = None
    params = preprocess_text_params_positive()
    error = error_setting.TooFewColumnsInDatasetError
    msg = r'Number of columns in input dataset "Dataset" is less ' \
          r'than allowed minimum of 1 column\(s\).'
    return dataset, stopwords, params, error, msg


def _gen_invalid_column_type():
    dataset = DataTable(pd.DataFrame({TargetColumnName: [1, 2, 3]}))
    stopwords = None
    params = preprocess_text_params_positive()
    error = error_setting.InvalidColumnTypeError
    msg = "Cannot process column \"text\" of type Numeric. The type is not supported by the " \
          "module. Parameter name: Text column to clean."
    return dataset, stopwords, params, error, msg


def _gen_invalid_selected_column_number():
    dataset = DataTable(pd.DataFrame({'col1': ['a', 'b', 'c'], 'col2': ['A', 'B', 'C']}))
    stopwords = None
    params = preprocess_text_params_positive()
    error = error_setting.BadNumberOfSelectedColumnsError
    msg = r"Column selection pattern \"Text column to clean\" is expected to provide 1 column" \
          r"\(s\) selected in input dataset, but 2 column\(s\) is/are actually provided."
    return dataset, stopwords, params, error, msg


def _gen_null_column_selection():
    dataset = DataTable(pd.DataFrame({'col1': ['a', 'b', 'c'], 'col2': ['A', 'B', 'C']}))
    stopwords = None
    params = preprocess_text_params_positive()
    params['text_column'] = None
    error = error_setting.NullOrEmptyError
    msg = "Input \"Text column to clean\" is null or empty."
    return dataset, stopwords, params, error, msg


def _gen_multi_column_stopwords():
    dataset = DataTable(pd.DataFrame({'text': ['Hello world!']}))
    stopwords = DataTable(pd.DataFrame({'col1': ['a', 'b', 'c'], 'col2': ['d', 'e', 'f']}))
    params = preprocess_text_params_positive()
    error = error_setting.UnexpectedNumberOfColumnsError
    msg = r"In input dataset \"Stop words\", expected \"1\" column\(s\)" \
          r" but found \"2\" column\(s\) instead."
    return dataset, stopwords, params, error, msg


def _gen_invalid_type_stopwords():
    dataset = DataTable(pd.DataFrame({'text': ['Hello world!']}))
    stopwords = DataTable(pd.DataFrame({'col1': [1, 2, 3]}))
    params = preprocess_text_params_positive()
    error = error_setting.InvalidColumnTypeError
    msg = "Cannot process column \"col1\" of type Numeric. The type is not supported by the " \
          "module. Parameter name: Stop words."
    return dataset, stopwords, params, error, msg


def _gen_invalid_custom_regular_expression():
    dataset = DataTable(pd.DataFrame({'text': ['Hello word!']}))
    stopwords = None
    params = preprocess_text_params_positive()
    params['custom_expression'] = ".*!"
    params['custom_replacement'] = "\\"
    error = error_setting.FailedToCompleteOperationError
    msg = "Error while completing operation: \"apply custom regular expression\"."
    return dataset, stopwords, params, error, msg


@pytest.mark.parametrize('dataset,stopwords,params,output_ref', [
    _gen_english_smoke_test(),
    _gen_remove_stopwords(),
    _gen_detect_sentences(),
    _gen_remove_numbers(),
    _gen_remove_special_characters(),
    _gen_remove_duplicate_characters(),
    _gen_remove_emails(),
    _gen_remove_urls(),
    _gen_expand_verb_contractions(),
    _gen_normalize_backslashes(),
    _gen_split_tokens_by_chars(),
    _gen_non_null_custom_expression(),
    _gen_null_custom_expression(),
    _gen_missing_input_dataset(),
    _gen_mix_type_dataset()
])
def test_valid_case(dataset, stopwords, params, output_ref):
    documents_df = pd.DataFrame(dataset, columns=[TargetColumnName])
    dataset = DataTable(documents_df)
    if stopwords:
        stopwords = DataTable(pd.DataFrame(stopwords, columns=[StopwordsColumnName]))
    output_refdf = pd.concat([documents_df, pd.DataFrame(output_ref, columns=[
        f"{PreprocessTextConstant.PreprocessedColumnPrefix} {TargetColumnName}"])], axis=1)
    output = PreprocessTextModule.run(dataset=dataset, stopwords=stopwords, **params)[0]
    assert output.data_frame.equals(output_refdf)


@pytest.mark.parametrize('dataset,stopwords,params,error,msg', [
    _gen_null_dataset(),
    _gen_zero_row_dataset(),
    _gen_empty_dataset(),
    _gen_invalid_column_type(),
    _gen_invalid_selected_column_number(),
    _gen_null_column_selection(),
    _gen_multi_column_stopwords(),
    _gen_invalid_type_stopwords(),
    _gen_invalid_custom_regular_expression()
])
def test_error_case(dataset, stopwords, params, error, msg):
    with pytest.raises(expected_exception=error, match=msg):
        PreprocessTextModule.run(dataset=dataset, stopwords=stopwords, **params)


def test_preprocess_text_repeatedly():
    # Verify if generates multi preprocessed column when repeatedly preprocess the same dataset
    dataset = DataTable(pd.DataFrame({TargetColumnName: ["This is a simple text."]}))
    stopwords = None
    params = preprocess_text_params_negative()
    params['text_column'] = DataTableColumnSelectionBuilder().include_col_names(TargetColumnName).build()
    output = PreprocessTextModule.run(dataset=dataset, stopwords=stopwords, **params)[0]
    output = PreprocessTextModule.run(dataset=output, stopwords=stopwords, **params)[0]
    output_refdf = pd.DataFrame(
        [["This is a simple text.", "This is a simple text .", "This is a simple text ."]],
        columns=[TargetColumnName,
                 f"{PreprocessTextConstant.PreprocessedColumnPrefix} {TargetColumnName}",
                 f"{PreprocessTextConstant.PreprocessedColumnPrefix} {TargetColumnName} 1"])
    assert output.data_frame.equals(output_refdf)


def test_imported_dataset():
    # Verify if works with imported data when all options are true
    script_dir = os.path.dirname(os.path.abspath(__file__))
    large_data_path = os.path.join(script_dir, 'input', 'book_reviews_from_amazon_large.csv')
    small_data_path = os.path.join(script_dir, 'input', 'book_reviews_from_amazon_small.csv')
    # large dataset is for local test
    if os.path.exists(large_data_path):
        data_path = large_data_path
    else:
        data_path = small_data_path
    dataset_df = pd.read_csv(data_path, header=None, names=['col1', TargetColumnName])
    dataset = DataTable(dataset_df)
    stopwords = None
    params = preprocess_text_params_positive()
    params['text_column'] = DataTableColumnSelectionBuilder().include_col_names(TargetColumnName).build()
    output = PreprocessTextModule.run(dataset=dataset, stopwords=stopwords, **params)[0]
    assert len(output.data_frame) == len(dataset_df)
