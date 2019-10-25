import pickle
import unittest
import collections
import numpy as np
import pandas as pd
from io import BytesIO
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import fetch_20newsgroups
from azureml.automl.core.sweeping.meta_sweeper import MetaSweeper
from azureml.automl.core.configuration import SweeperConfig
import azureml.automl.core.featurization as pp
from azureml.automl.core.featurizer.transformer import TextFeaturizers
from azureml.automl.core.featurizer.transformer.text import BiLSTMAttentionTransformer
from azureml.automl.core.featurizer.transformer.featurization_utilities import if_package_exists


def check_pickleable(obj):
    try:
        with BytesIO() as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        return True
    except Exception:
        return False


class MetaSweeperTest:

    bilstm_dnn_sweeper = {
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
                        "embeddings_name": "glove_6B_300d_word2vec"
                    }
                }
            ],
            "include_baseline": True
        },
        "column_purposes": [
            {
                "group": "featurize",
                "types": ["text"]
            }
        ],
        "epsilon": -1.0,
    }


class TestBiLSTMTransformer(BiLSTMAttentionTransformer):
    """ Instantiate ptdnn without downloading model. """

    def __init__(self, provider):
        super(TestBiLSTMTransformer, self).__init__(provider)

    def fit(self, X, y, **kwargs):
        return self

    def transform(self, X, y=None, **kwargs):
        return np.zeros((len(X), 306))


class MetaSweeperStub(MetaSweeper):
    def __init__(self, task, timeout_sec=MetaSweeper.DEFAULT_SWEEPER_TIMEOUT_SEC,
                 config_override=None):
        self._config_override = config_override

        super(MetaSweeperStub, self).__init__(task, timeout_sec, enable_dnn=True)

    def _get_config(self):
        # override the default config to make sure we use feature sweeping
        default_cfg = SweeperConfig.default()
        if self._config_override is not None:
            return MetaSweeperStub.merge_dict(default_cfg, self._config_override)
        return default_cfg

    @staticmethod
    def merge_dict(left, right):
        for k, v in right.items():
            if isinstance(v, collections.Mapping):
                left[k] = MetaSweeperStub.merge_dict(left.get(k, {}), v)
            else:
                left[k] = v
        return left


class DeterministicSweeper():

    def __init__(self, meta_sweeper, config_experiment_to_force):
        self.meta_sweeper = meta_sweeper
        self.config_experiment_to_force = config_experiment_to_force

    def sweep(self, df, y, stats_and_column_purposes):
        pipes = self.meta_sweeper._build_featurizers(self.config_experiment_to_force, None)
        pipes.steps[-1] = (pipes.steps[-1][0], TestBiLSTMTransformer(None))  # Replace with mock bi_lstm
        return [(list(df.columns), pipes)]


class DeterministicDataTransformer(pp.DataTransformer):
    def __init__(self, *args, deterministic_feature_sweeper=None, **kwargs):
        super(DeterministicDataTransformer, self).__init__(*args, **kwargs)
        self.deterministic_feature_sweeper = deterministic_feature_sweeper

    def _perform_feature_sweeping(self, df, y,
                                  stats_and_column_purposes,
                                  all_new_column_names,
                                  feature_sweeper=None):
        return super(DeterministicDataTransformer, self)._perform_feature_sweeping(
            df, y,
            stats_and_column_purposes,
            all_new_column_names,
            feature_sweeper=self.deterministic_feature_sweeper)


def get_data():
    removedata = ('headers', 'footers', 'quotes')
    categories = ['sci.space', 'talk.religion.misc']
    data_train = fetch_20newsgroups(subset='test',
                                    categories=categories,
                                    shuffle=True,
                                    random_state=42,
                                    remove=removedata)
    sampled_X = data_train.data[:25]
    X2cols = []
    for doc in sampled_X:
        doc1 = doc[:30]
        doc2 = doc[-30:]
        X2cols.append([doc1, doc2])
    sampled_y = data_train.target[:25]
    columns = ['a', 'b']
    X = pd.DataFrame(X2cols, columns=columns)
    y = sampled_y
    return X, y


def get_bilstm_in_datatransformer():
    X, y = get_data()
    columns = list(X.columns)

    config = {
        "classification": {
            "sweeping_enabled": True,
            "page_sampled_data_to_disk": True,
            "run_sweeping_in_isolation": False,
            "enabled_sweepers": [MetaSweeperTest.bilstm_dnn_sweeper]
        }
    }
    meta_sweeper = MetaSweeperStub("classification", config_override=config)
    deterministic_feature_sweeper = DeterministicSweeper(
        meta_sweeper,
        config['classification']['enabled_sweepers'][0]['experiment'])

    transformer = DeterministicDataTransformer(
        "classification",
        deterministic_feature_sweeper=deterministic_feature_sweeper,
        enable_dnn=True,
        enable_feature_sweeping=True)
    _ = transformer.fit_transform(X, y)

    return transformer, columns


class TestBiLSTMAttentionTransformer(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self._device = "cpu"
        super(TestBiLSTMAttentionTransformer, self).__init__(*args, **kwargs)

    @if_package_exists("test_bilstm_early_stopping", ["torch", "spacy", "en_core_web_sm"])
    def test_bilstm_early_stopping(self):
        """Tests that early stopping logic works
        """
        from azureml.automl.core.featurizer.transformer.text.bilstm_attention_transformer import EarlyStopping

        es = EarlyStopping(patience=2, delta=0.0)
        valid_accuracies = [1., 2., 3., 4., 3., 5., 4., 2.5, 6.]
        # Should early stop at 7th reading (first reading's index = 0), with accuracy 2.5

        for i, valid_accuracy in enumerate(valid_accuracies):
            if es.check_early_stop_train(valid_accuracy):
                stopIndex = i
                stopAccuracy = valid_accuracy
                break

        assert stopIndex == 7 and np.isclose(stopAccuracy, 2.5), "Early stopping failed"

    @if_package_exists("test_bilstm_attention_pred", ["torch", "spacy", "en_core_web_sm"])
    def test_bilstm_attention_pred(self):
        """Tests on a sample test sentence in a pipeline"""

        # Test GloVe embeddings download
        from azureml.automl.core.featurizer.transformer.text.bilstm_attention_transformer import WordEmbed
        word_embedding = WordEmbed(embeddings_name="glove_6B_300d_word2vec")
        assert word_embedding is not None

        from azureml.automl.core.featurizer.transformer.text.bilstm_attention_transformer \
            import BiLSTMAttentionTransformer
        bi_lstm = BiLSTMAttentionTransformer(epochs=1, batch_size=32,
                                             do_early_stopping=True,
                                             device=self._device, seed=42)

        X = np.array(["hello world", "the world is all that is the case",
                      "a Quick Brown fox blah blah", "King and the Queen",
                      "hello world", "the world is all that is the case",
                      "a Quick Brown fox blah blah", "King and the Queen",
                      "hello world", "the world is all that is the case"])
        y = np.array([0, 1, 0, 1, 1, 1, 0, 0, 1, 1])

        # Used as a sklearn transformer in a Pipeline
        clf = Pipeline([('bi_lstm', bi_lstm),
                        ('clf', LogisticRegression(solver='lbfgs'))])
        clf.fit(X, y)
        y_preds = clf.predict(X)
        assert len(y_preds) == len(X)

        X_multicol = np.array([["hello world", "yes it is"],
                               ["the world is all that is the case", 5],
                               ["a Quick Brown fox blah blah", 3],
                               [99, "News"],
                               ["This", "that"],
                               ["very good", "not bad"],
                               ["not Too bad", "acceptable"],
                               ["great", "fine"],
                               ["Conference", "science"],
                               ["arts", "music"],
                               ["history", "geography"],
                               ["King and the qUeen", "Dog and cat"]])

        y_multicol = np.array([0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0])

        # Used as a sklearn transformer in a Pipeline
        clf = Pipeline([('bi_lstm', bi_lstm),
                        ('clf', LogisticRegression(solver='lbfgs'))])
        clf.fit(X_multicol, y_multicol)
        y_preds = clf.predict(X_multicol)
        assert len(y_preds) == len(X_multicol)

        # Test fit and transform outside of scikits pipeline
        model = bi_lstm.fit(X, y)
        X_transformed = model.transform(X)
        assert np.isclose(np.sum(X_transformed), -2.3182354)

        # Test fit_transform outside of scikits pipeline
        X_transformed = bi_lstm.fit_transform(X, y)
        assert np.isclose(np.sum(X_transformed), -2.3182354)

        # Pickle test
        check_pickleable(bi_lstm)

        # Engineered feature names test
        tr, cols = get_bilstm_in_datatransformer()
        name_last = tr.get_engineered_feature_names()[-1]
        err_msg = "BiLSTM eng. features names are broken. Eg eng. feature name = {}".format(name_last)
        assert name_last == "_".join(cols) + '_StringConcatTransformer_TestBiLSTMTransformer_305', err_msg

        # Ensure that if the download fails an exception is raised
        bi_lstm = TextFeaturizers.bilstm_text_dnn(embeddings_name="glove_6B_300d_word2vec")
        bi_lstm._embeddings_name = "weird-embedding"
        with self.assertRaises(Exception):
            bi_lstm.fit(X, y)


if __name__ == "__main__":
    unittest.main()
