from typing import Any, Dict, Optional
from unittest.mock import patch
import logging
import os
import unittest

from sklearn.datasets import fetch_20newsgroups, make_classification
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn_pandas import DataFrameMapper
import numpy as np
import pandas as pd

from azureml.automl.core.column_purpose_detection import ColumnPurposeDetector
from azureml.automl.core.constants import SupportedTransformersInternal
from azureml.automl.core.configuration.sampler_config import SamplerConfig
from azureml.automl.core.sweeping.meta_sweeper import MetaSweeper
from automl.client.core.common import constants
from azureml.automl.core.featurizer.transformer.featurization_utilities import if_package_exists
import azureml.automl.core.featurization as pp
from ..utilities import MockAutoMLFeatureConfigManager


class MetaSweeperStub(MetaSweeper):
    def __init__(self, task: str,
                 timeout_sec: int = MetaSweeper.DEFAULT_SWEEPER_TIMEOUT_SEC,
                 config_overrides: Optional[Dict[str, Any]] = None,
                 enable_dnn: bool = True,
                 is_cross_validation: bool = False,
                 featurization_config: Optional[pp.FeaturizationConfig] = None) -> None:
        self._config_overrides = config_overrides

        feature_sweeping_config = MockAutoMLFeatureConfigManager(self._config_overrides)\
            .get_feature_sweeping_config(task_type=task)
        super(MetaSweeperStub, self).__init__(task=task,
                                              timeout_sec=timeout_sec,
                                              enable_dnn=enable_dnn,
                                              is_cross_validation=is_cross_validation,
                                              feature_sweeping_config=feature_sweeping_config)

# Uncomment following lines when Pytest support is added to these tests
# @pytest.mark.parametrize('config_overrides', [
#     {"sweeping_enabled": True, "page_sampled_data_to_disk": True, "run_sweeping_in_isolation": True},
#     {"sweeping_enabled": True, "page_sampled_data_to_disk": True, "run_sweeping_in_isolation": False}])


def _test_sweep(task, config_overrides, result_expected=True, row_counts=300, enable_dnn=True,
                transformer_name=None, is_cross_validation=False, featurization_config=None):
    removedata = ('headers', 'footers', 'quotes')
    categories = ['alt.atheism', 'talk.religion.misc', 'comp.graphics', 'sci.space']

    # TODO: fetch some regression dataset for regression tasks
    data_train = fetch_20newsgroups(subset='test', categories=categories, shuffle=True, random_state=42,
                                    remove=removedata)
    sampled_X = data_train.data[:row_counts]
    sampled_y = data_train.target[:row_counts]
    X = pd.DataFrame(sampled_X)
    y = sampled_y
    stats_and_column_purposes = ColumnPurposeDetector.get_raw_stats_and_column_purposes(X)
    if task != constants.Tasks.CLASSIFICATION:
        # transform the y so that this dataset acts like a regression one
        clf = Pipeline([('pre', CountVectorizer()), ('clf', LogisticRegression())])
        clf.fit(sampled_X, y)
        y = clf.decision_function(sampled_X)[:, 0]

    meta_sweeper = MetaSweeperStub(task, config_overrides=config_overrides, enable_dnn=enable_dnn,
                                   featurization_config=featurization_config, is_cross_validation=is_cross_validation)
    ret = meta_sweeper.sweep(X, y, stats_and_column_purposes)
    print("Added sweepers are: " + str(ret) if ret is not None else "None")
    if result_expected:
        assert ret is not None
        assert len(ret) > 0
        # Check transformer_name occurs in the list of transformers swept over
        if transformer_name is not None:
            assert str(ret).__contains__(transformer_name)
    else:
        assert len(ret) == 0


def _load_dataset(dataset_name='newsgroup20'):
    if dataset_name == 'dummy':
        return _load_dummy_classification()
    elif dataset_name == 'newsgroup20':
        return _load_newsgroup20_sampled()


def _load_dummy_classification():
    sampled_X, sampled_y = make_classification()
    categories = ['cat1', 'cat2', 'cat3']

    # Add 10 random categorical data
    cat_data_1 = np.array([categories[y] for y in sampled_y])
    cat_data_2 = np.array([categories[y] for y in sampled_y])
    sampled_X = np.hstack((sampled_X, cat_data_1.reshape(sampled_X.shape[0], 1),
                           cat_data_2.reshape(sampled_X.shape[0], 1)))

    return sampled_X, sampled_y


def _load_newsgroup20_sampled():
    removedata = ('headers', 'footers', 'quotes')
    categories = ['alt.atheism', 'talk.religion.misc', 'comp.graphics', 'sci.space']
    data_train = fetch_20newsgroups(subset='test', categories=categories, shuffle=True, random_state=42,
                                    remove=removedata)
    sampled_X = data_train.data[:300]
    sampled_y = data_train.target[:300]
    return sampled_X, sampled_y


def _test_engineering_feature_names(task, config_overrides, dataset_name='newsgroup20'):
    sampled_X, sampled_y = _load_dataset(dataset_name)
    X = pd.DataFrame(sampled_X)
    y = sampled_y
    stats_and_column_purposes = ColumnPurposeDetector.get_raw_stats_and_column_purposes(X)
    if task != constants.Tasks.CLASSIFICATION:
        # transform the y so that this dataset acts like a regression one
        clf = Pipeline([('pre', CountVectorizer()), ('clf', LogisticRegression())])
        clf.fit(sampled_X, y)
        y = clf.decision_function(sampled_X)[:, 0]

    meta_sweeper = MetaSweeperStub(task, config_overrides=config_overrides)

    transformer = pp.DataTransformer("classification",
                                     enable_feature_sweeping=True,
                                     feature_sweeping_config=meta_sweeper._cfg)
    transforms_list = transformer._get_transforms(X, stats_and_column_purposes, y)
    new_column_names = ['C1']
    transforms_list = transformer._perform_feature_sweeping(
        X, y, stats_and_column_purposes, new_column_names, meta_sweeper)
    assert len(transforms_list) > 0
    transformer.mapper = DataFrameMapper(transforms_list, input_df=True, sparse=True)
    transformer.fit_transform(X)
    feature_names = transformer.get_engineered_feature_names()
    assert len(feature_names) > 0
    for name in feature_names:
        assert (name.startswith('C1_'))


class MetaSweeperTest(unittest.TestCase):
    # create a classification sweeper where we know the experiment is going to win over the baseline
    # based on the test dataset we're using here
    classification_sweeper = {
        "name": "TextWordEmbeddings",
        "type": "binary",
        "enabled": True,
        "sampler": {
            "id": "count",
            "args": [],
            "kwargs": {}
        },
        "estimator": "logistic_regression",
        "scorer": "accuracy",
        "experiment": {
            "featurizers": [
                {
                    "id": "string_cast",
                    "type": "text"
                },
                {
                    "id": "bow_transformer",
                    "type": "text"
                }
            ]
        },
        "baseline": {
            "featurizers": [
                {
                    "id": "string_cast",
                    "type": "text"
                },
                {
                    "id": "word_embeddings",
                    "type": "text",
                    "args": [],
                    "kwargs": {
                        "embeddings_name": "wiki_news_300d_1M_subword",
                        "only_run_on_cpu": False,
                    }
                }
            ],
            "include_baseline": True
        },
        "column_purposes": [
            {
                "group": False,
                "types": ["text"]
            }
        ],
        "epsilon": 0.01
    }

    nonconcat_bert_sweeper = {
        "name": "PreTrainedDNNEmbeddings",
        "type": "binary",
        "enabled": True,
        "sampler": {
            "id": "count",
            "args": [],
            "kwargs": {}
        },
        "estimator": "logistic_regression",
        "scorer": "accuracy",
        "baseline": {
            "featurizers": [
                {
                    "id": "string_cast",
                    "type": "text"
                },
                {
                    "id": "bow_transformer",
                    "type": "text"
                }
            ]
        },
        "experiment": {
            "featurizers": [
                {
                    "id": "string_cast",
                    "type": "text"
                },
                {
                    "id": "pretrained_text_dnn",
                    "type": "text",
                            "args": [],
                            "kwargs": {
                                "model_name": "bert-base-uncased",
                                "can_run_on_cpu": False
                            }
                }
            ],
            "include_baseline": True
        },
        "column_purposes": [
            {
                "group": False,
                "types": ["text"]
            }
        ],
        "epsilon": 0.01
    }

    word_embedding_concat_sweeper = {
        "name": "TextWordEmbeddingsConcat",
        "enabled": True,
        "type": "binary",
        "sampler": {
            "id": "count",
            "args": [],
            "kwargs": {}
        },
        "estimator": "logistic_regression",
        "scorer": "accuracy",
        "experiment_result_override": True,
        "baseline": {
            "featurizers": [
                {
                    "id": "string_cast",
                    "type": "text"
                },
                {
                    "id": "string_concat",
                    "type": "text"
                },
                {
                    "id": "bow_transformer",
                    "type": "text"
                }
            ]
        },
        "experiment": {
            "featurizers": [
                {
                    "id": "string_cast",
                    "type": "text"
                },
                {
                    "id": "string_concat",
                    "type": "text"
                },
                {
                    "id": "word_embeddings",
                    "type": "text",
                    "args": [],
                    "kwargs": {
                        "embeddings_name": "wiki_news_300d_1M_subword",
                        "only_run_on_cpu": False,
                    }
                }
            ],
            "include_baseline": True
        },
        "column_purposes": [{
            "group": "featurize",
            "types": ["text"],
        }],
        "epsilon": 0.01
    }

    lstm_sweeper = {
        "name": "BiLSTMTextEmbeddings",
        "enabled": True,
        "type": "binary",
        "sampler": {
            "id": "count",
            "args": [],
            "kwargs": {}
        },
        "estimator": "logistic_regression",
        "scorer": "accuracy",
        "experiment_result_override": True,
        "baseline": {
            "featurizers": [
                {
                    "id": "string_cast",
                    "type": "text"
                },
                {
                    "id": "string_concat",
                    "type": "text"
                },
                {
                    "id": "bow_transformer",
                    "type": "text"
                }
            ]
        },
        "experiment": {
            "featurizers": [
                {
                    "id": "string_cast",
                    "type": "text"
                },
                {
                    "id": "string_concat",
                    "type": "text"
                },
                {
                    "id": "bilstm_text_dnn",
                    "type": "text",
                    "args": [],
                    "kwargs": {
                        "embeddings_name": "glove_6B_300d_word2vec",
                        "can_run_on_gpu": True,
                    }
                }],
            "include_baseline": True
        },
        "column_purposes": [{
            "group": "featurize",
            "types": ["text"],
        }],
        "epsilon": 0.0
    }

    cvte_sweeper = {
        "name": "CategoricalTargetEncoder",
        "type": "binary",
        "enabled": True,
        "sampler": {
            "id": "count",
            "args": [],
            "kwargs": {}
        },
        "estimator": "logistic_regression",
        "scorer": "accuracy",
        "baseline": {
            "featurizers": [
                {
                    "id": "cat_imputer",
                    "type": "categorical"
                },
                {
                    "id": "string_cast",
                    "type": "text"
                },
                {
                    "id": "count_vectorizer",
                    "type": "text"
                }
            ]
        },
        "experiment": {
            "featurizers": [
                {
                    "id": "cat_imputer",
                    "type": "categorical"
                },
                {
                    "id": "string_cast",
                    "type": "text"
                },
                {
                    "id": "cat_targetencoder",
                    "type": "categorical",
                    "args": [],
                    "kwargs": {
                        "task": "classification"
                    }
                }
            ],
            "include_baseline": False
        },
        "column_purposes": [
            {
                "group": "score",
                "types": ["categorical"],
            }
        ],
        "epsilon": 0.01
    }

    word_embeddings_sweeper = {
        "name": "TextWordEmbeddings",
        "type": "binary",
        "enabled": True,
        "sampler": {
            "id": "count",
            "args": [],
            "kwargs": {}
        },
        "estimator": "logistic_regression",
        "scorer": "accuracy",
        "baseline": {
            "featurizers": [
                {
                    "id": "string_cast",
                    "type": "text"
                },
                {
                    "id": "word_embeddings",
                    "type": "text",
                    "args": [],
                    "kwargs": {
                        "embeddings_name": "wiki_news_300d_1M_subword",
                        "only_run_on_cpu": False,
                    }
                }
            ]
        },
        "experiment": {
            "featurizers": [
                {
                    "id": "string_cast",
                    "type": "text"
                },
                {
                    "id": "word_embeddings",
                    "type": "text",
                    "args": [],
                    "kwargs": {
                        "embeddings_name": "wiki_news_300d_1M_subword",
                        "only_run_on_cpu": False,
                    }
                }
            ],
            "include_baseline": True
        },
        "column_purposes": [
            {
                "group": False,
                "types": ["text"],
            }
        ],
        "epsilon": 0.0001
    }

    word_embeddings_sweeper_disabled = {
        "name": "TextWordEmbeddings",
        "type": "binary",
        "enabled": False,
        "sampler": {
            "id": "count",
            "args": [],
            "kwargs": {}
        },
        "estimator": "logistic_regression",
        "scorer": "accuracy",
        "baseline": {
            "featurizers": [
                {
                    "id": "string_cast",
                    "type": "text"
                },
                {
                    "id": "word_embeddings",
                    "type": "text",
                    "args": [],
                    "kwargs": {
                        "embeddings_name": "wiki_news_300d_1M_subword",
                    }
                }
            ]
        },
        "experiment": {
            "featurizers": [
                {
                    "id": "string_cast",
                    "type": "text"
                },
                {
                    "id": "word_embeddings",
                    "type": "text",
                    "args": [],
                    "kwargs": {
                        "embeddings_name": "wiki_news_300d_1M_subword",
                    }
                }
            ],
            "include_baseline": True
        },
        "column_purposes": [
            {
                "group": False,
                "types": ["text"],
            }
        ],
        "epsilon": 0.0001
    }

    def test_classification_sweep_isolation(self):
        config = {
            "classification": {
                "sweeping_enabled": True,
                "page_sampled_data_to_disk": True,
                "run_sweeping_in_isolation": True,
                "enabled_sweepers": [MetaSweeperTest.classification_sweeper]
            }
        }
        _test_sweep(constants.Tasks.CLASSIFICATION, config)

    def test_classification_sweep_same_process(self):
        config = {
            "classification": {
                "sweeping_enabled": True,
                "page_sampled_data_to_disk": True,
                "run_sweeping_in_isolation": False,
                "enabled_sweepers": [MetaSweeperTest.classification_sweeper]
            }
        }
        _test_sweep(constants.Tasks.CLASSIFICATION, config)

    def test_classification_force_win(self):
        config = {
            "classification": {
                "sweeping_enabled": True,
                "page_sampled_data_to_disk": True,
                "run_sweeping_in_isolation": True,
                "enabled_sweepers": [MetaSweeperTest.nonconcat_bert_sweeper,
                                     MetaSweeperTest.word_embedding_concat_sweeper]
            }
        }
        _test_sweep(constants.Tasks.CLASSIFICATION, config, transformer_name="wordembeddingtransformer")

    def test_regression_sweep_same_process(self):
        config = {
            "regression": {
                "sweeping_enabled": True,
                "page_sampled_data_to_disk": True,
                "run_sweeping_in_isolation": False
            }
        }
        _test_sweep(constants.Tasks.REGRESSION, config)

    def test_regression_sweep_isolation(self):
        config = {
            "regression": {
                "sweeping_enabled": True,
                "page_sampled_data_to_disk": True,
                "run_sweeping_in_isolation": True
            }
        }
        _test_sweep(constants.Tasks.REGRESSION, config)

    def test_blocked_transformers(self):
        config = {
            "classification": {
                "sweeping_enabled": True,
                "page_sampled_data_to_disk": True,
                "run_sweeping_in_isolation": False,
                "enabled_sweepers": [MetaSweeperTest.classification_sweeper]
            }
        }
        blocked_transformers = [SupportedTransformersInternal.WordEmbedding]
        featurization_config = pp.FeaturizationConfig(blocked_transformers=blocked_transformers)
        _test_sweep(constants.Tasks.CLASSIFICATION, config, featurization_config=featurization_config)

    def test_build_sampler(self):
        cfg = {
            "id": "count",
            "args": [],
            "kwargs": {
                "min_examples_per_class": 100
            }
        }

        feature_config_manager = MockAutoMLFeatureConfigManager()
        feature_sweeping_config = feature_config_manager.get_feature_sweeping_config(task_type="classification")
        s = MetaSweeper("classification", feature_sweeping_config=feature_sweeping_config).\
            _build_sampler(SamplerConfig.from_dict(cfg), task="classification", logger=logging.getLogger(""))
        assert s is not None
        assert s._min_examples_per_class == 100

    @if_package_exists("test_classification_sweep_bilstm", ["torch", "spacy", "en_core_web_sm"])
    def test_classification_sweep_bilstm(self):
        config = {
            "classification": {
                "sweeping_enabled": True,
                "page_sampled_data_to_disk": True,
                "run_sweeping_in_isolation": True,
                "enabled_sweepers": [MetaSweeperTest.lstm_sweeper]
            }
        }
        _test_sweep(constants.Tasks.CLASSIFICATION, config, row_counts=50, enable_dnn=True,
                    transformer_name="BiLSTMAttentionTransformer")

    @if_package_exists("test_classification_no_sweep_bilstm_if_cv", ["torch", "spacy", "en_core_web_sm"])
    def test_classification_no_sweep_bilstm_if_cv(self):
        config = {
            "classification": {
                "sweeping_enabled": True,
                "page_sampled_data_to_disk": True,
                "run_sweeping_in_isolation": False,
                "enabled_sweepers": [MetaSweeperTest.lstm_sweeper]
            }
        }
        _test_sweep(constants.Tasks.CLASSIFICATION, config, row_counts=300,
                    result_expected=False, is_cross_validation=True)

    @if_package_exists("test_disable_sweeping_bilstm", ["torch", "spacy", "en_core_web_sm"])
    def test_disable_sweeping_bilstm(self):
        config = {
            "classification": {
                "sweeping_enabled": True,
                "page_sampled_data_to_disk": True,
                "run_sweeping_in_isolation": False,
                "enabled_sweepers": [MetaSweeperTest.lstm_sweeper]
            }
        }
        _test_sweep(constants.Tasks.CLASSIFICATION, config,
                    result_expected=False, enable_dnn=False)

    @if_package_exists("test_classification_no_sweep_bilstm_if_cv_enable_isolation",
                       ["torch", "spacy", "en_core_web_sm"])
    def test_classification_no_sweep_bilstm_if_cv_enable_isolation(self):
        config = {
            "classification": {
                "sweeping_enabled": True,
                "page_sampled_data_to_disk": True,
                "run_sweeping_in_isolation": True,
                "enabled_sweepers": [MetaSweeperTest.lstm_sweeper]
            }
        }
        _test_sweep(constants.Tasks.CLASSIFICATION, config, row_counts=300,
                    result_expected=False, is_cross_validation=True)

    @unittest.skip("Failing in generated feature name")
    def test_classification_test_engineering_feature_names_wordembedding(self):
        config = {
            "classification": {
                "sweeping_enabled": True,
                "page_sampled_data_to_disk": True,
                "run_sweeping_in_isolation": False,
                "enabled_sweepers": [MetaSweeperTest.word_embeddings_sweeper]
            }
        }
        _test_engineering_feature_names(constants.Tasks.CLASSIFICATION, config)

        def test_multisweeper_pickling(self):
            import tempfile
            import pickle
            temp_file = tempfile.mktemp()
            with open(temp_file, mode='wb', buffering=1) as ck_file:
                for col in range(10):
                    ck_file.write(pickle.dumps((col, col)))

            with open(temp_file, mode='rb') as ck_file:
                i = 0
                for row in ck_file:
                    s_idx, col_idx = pickle.loads(row)
                    assert s_idx == col_idx == i
                    i = i + 1

            os.remove(temp_file)

    @unittest.skip("Failing in generated feature name")
    @patch('automl.client.core.common.scoring.classification_scorer.ClassificationScorer.'
           'is_experiment_better_than_baseline')
    def test_classification_test_engineering_feature_names_cvte(self, mock_scorer):
        config = {
            "classification": {
                "sweeping_enabled": True,
                "page_sampled_data_to_disk": True,
                "run_sweeping_in_isolation": False,
                "enabled_sweepers": [MetaSweeperTest.cvte_sweeper]
            }
        }
        mock_scorer.return_value = True
        _test_engineering_feature_names(constants.Tasks.CLASSIFICATION, config, dataset_name='dummy')

    def test_sweeper_disabling(self):
        config = {
            "classification": {
                "sweeping_enabled": True,
                "page_sampled_data_to_disk": True,
                "run_sweeping_in_isolation": False,
                "enabled_sweepers": [MetaSweeperTest.word_embeddings_sweeper_disabled]
            }
        }

        _test_sweep(constants.Tasks.CLASSIFICATION, config, False)


if __name__ == '__main__':
    unittest.main()
