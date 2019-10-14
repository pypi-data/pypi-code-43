from sklearn.metrics import accuracy_score
from sklearn.datasets import fetch_20newsgroups
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

import azureml.automl.core.featurization as pp
from azureml.automl.core.sweeping.meta_sweeper import MetaSweeper
from azureml.automl.core.configuration import SweeperConfig

from azureml.automl.core.featurizer.transformer.featurization_utilities import if_package_exists
from azureml.automl.core.featurizer.transformer import TextFeaturizers
from azureml.automl.core.featurizer.transformer.text import PretrainedTextDNNTransformer
import unittest
import pickle
from io import BytesIO

import numpy as np
import pandas as pd
import os
import shutil
import collections


def get_train_val_data_for_20news(train_size=0.3, test_size=0.7):

    remove = ('headers', 'footers', 'quotes')
    categories = [
        'alt.atheism',
        'talk.religion.misc',
        'comp.graphics',
        'sci.space',
    ]
    data_train = fetch_20newsgroups(subset='train', categories=categories,
                                    shuffle=True, random_state=42,
                                    remove=remove)

    X_train, X_valid, y_train, y_valid =\
        train_test_split(data_train.data, data_train.target,
                         train_size=train_size, test_size=test_size,
                         random_state=42)
    return X_train, X_valid, y_train, y_valid


def run_train_on_pipeline(ptd_trans):
    clf = Pipeline([('pre', ptd_trans),
                    ('clf', LogisticRegression(C=0.1, solver='lbfgs',
                                               multi_class='multinomial'))])
    X_train, X_valid, y_train, y_valid = get_train_val_data_for_20news()

    print("train and valid shapes: ", y_train.shape, y_valid.shape)
    clf.fit(X_train, y_train, pre__X_valid=X_valid, pre__y_valid=y_valid)
    return clf, X_valid, y_valid


def run_inference_and_assert_results(clf, X_valid, y_valid,
                                     acc_threshold=0.65):
    ypred_scikit = clf.predict(X_valid)
    ypred_pure_dnn = clf.steps[0][1].predict(X_valid)
    acc_score_scikit = accuracy_score(y_valid, ypred_scikit)
    acc_score_pure_dnn = accuracy_score(y_valid, ypred_pure_dnn)

    test_res0 = acc_score_scikit > acc_threshold
    test_res1 = acc_score_pure_dnn > acc_threshold
    print(
        "Transform+scikit accuracy of {acc_score_scikit} obtained on\
         subsample of 20news".format(acc_score_scikit=acc_score_scikit))
    print("Pure dnn accuracy of {acc_score_pure_dnn} obtained on\
    subsample of 20news".format(acc_score_pure_dnn=acc_score_pure_dnn))
    assert test_res0 and test_res1, "Did not sucessfully run on agnews\
     with accuracy above {}".format(acc_threshold)


def train_test(ptd_trans):
    """
    Train, classify, and get good score on some 20news group data.
    """
    clf, X_valid, y_valid = run_train_on_pipeline(ptd_trans)
    run_inference_and_assert_results(clf, X_valid, y_valid)


def train_test_infer1GPU(ptd_trans):
    """
    Train, classify, and get good score on some 20news group data.
    """
    clf, X_valid, y_valid = run_train_on_pipeline(ptd_trans)

    # Forcing the inference to happen only on one GPU, even if the training
    # was done using multiple GPUs
    clf.steps[0][1].n_gpu = 1

    run_inference_and_assert_results(clf, X_valid, y_valid)


def check_pickleable(obj):
    try:
        with BytesIO() as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        return True
    except Exception:
        return False


class MetaSweeperTest:

    pretrained_dnn_sweeper = {
        "name": "PreTrainedDNNEmbeddings",
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
                    "id": "pretrained_text_dnn",
                    "type": "text",
                    "args": [],
                    "kwargs": {
                          "model_name": "bert-base-uncased",
                          "can_run_on_cpu": True,
                          "max_steps": 1
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
        "epsilon": -1.0
    }


class TestPretrainedTextDNNTransformer(PretrainedTextDNNTransformer):
    """ Instantiate ptdnn without downloading model. """

    def __init__(self, provider):
        super(TestPretrainedTextDNNTransformer, self).__init__(provider)

    def fit(self, X, y, **kwargs):
        return self

    def transform(self, X, y=None, **kwargs):
        return np.zeros((len(X), 150))


class DeterministicSweeper():

    def __init__(self, meta_sweeper, config_experiment_to_force):
        self.meta_sweeper = meta_sweeper
        self.config_experiment_to_force = config_experiment_to_force

    def sweep(self, df, y, stats_and_column_purposes):
        pipes = self.meta_sweeper._build_featurizers(self.config_experiment_to_force, None)
        pipes.steps[-1] = (pipes.steps[-1][0], TestPretrainedTextDNNTransformer(None))  # Replace with mock ptdnn
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


class MetaSweeperStub(MetaSweeper):
    def __init__(self, task, timeout_sec=MetaSweeper.DEFAULT_SWEEPER_TIMEOUT_SEC,
                 config_override=None):
        self._config_override = config_override

        super(MetaSweeperStub, self).__init__(task, timeout_sec)

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


def get_data():
    removedata = ('headers', 'footers', 'quotes')
    categories = ['sci.space', 'talk.religion.misc']
    data_train = fetch_20newsgroups(subset='test', categories=categories, shuffle=True, random_state=42,
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


def get_bert_in_datatransformer():
    X, y = get_data()
    columns = list(X.columns)

    config = {
        "classification": {
            "sweeping_enabled": True,
            "page_sampled_data_to_disk": True,
            "run_sweeping_in_isolation": False,
            "enabled_sweepers": [MetaSweeperTest.pretrained_dnn_sweeper]
        }
    }
    meta_sweeper = MetaSweeperStub("classification", config_override=config)
    deterministic_feature_sweeper = DeterministicSweeper(
        meta_sweeper,
        config['classification']['enabled_sweepers'][0]['experiment'])

    transformer = DeterministicDataTransformer(
        "classification",
        deterministic_feature_sweeper=deterministic_feature_sweeper,
        enable_feature_sweeping=True)
    _ = transformer.fit_transform(X, y)
    return transformer, columns


class TestPretrainedTextDNN(unittest.TestCase):
    """ Test that bert/xlnet model can be downloaded
    and used as an automl Transformer."""

    def __init__(self, *args, **kwargs):
        super(TestPretrainedTextDNN, self).__init__(*args, **kwargs)

    @if_package_exists("test_PretrainedTextDNNTransformer", ["torch", "pytorch_transformers"])
    def test_bert_fit_transform_pickleable(self):
        config = {
            "classification": {
                "sweeping_enabled": True,
                "page_sampled_data_to_disk": True,
                "run_sweeping_in_isolation": False,
                "enabled_sweepers": [MetaSweeperTest.pretrained_dnn_sweeper]
            }
        }
        meta_sweeper = MetaSweeperStub("classification", config_override=config)
        ptdnn_bert = meta_sweeper._build_featurizers(
            config['classification']['enabled_sweepers'][0]['experiment'],
            None)

        # Test fit and concatenation logic for two rows
        X = np.array([["hello world", "yes it is"],
                      ["the world is all that is the case", 5],
                      ["a Quick Brown fox blah blah", 3]])
        y = np.array([0, 1, 0])

        # Used as a sklearn transformer in a Pipeline
        clf = Pipeline([('pre', ptdnn_bert),
                        ('clf', LogisticRegression(solver='lbfgs'))])
        clf.fit(X, y)
        y_preds = clf.predict(X)
        assert len(y_preds) == len(X)

        # Inspect output of fine-tuned bert directly
        X_transform = ptdnn_bert.transform(X)
        assert X_transform.shape == (3, 150), "Actual shape is {}".format(X_transform.shape)

        # Checksum of BERT output
        checksum = np.sum(X_transform)
        assert np.isclose(checksum, 22.378562927246094), "BERT checksum preds = {} are incorrect".format(checksum)

        # Test fit and concatenation logic for just one row
        X = np.array(["hello world", "the world is all that is the case",
                      "a Quick Brown fox blah blah", 3, 4])
        y = np.array([0, 1, 0, 1, 0])

        # Used as a sklearn transformer in a Pipeline
        clf = Pipeline([('pre', ptdnn_bert),
                        ('clf', LogisticRegression(solver='lbfgs'))])
        clf.fit(X, y)
        y_preds = clf.predict(X)
        assert len(y_preds) == len(X)

        # Pickle test
        check_pickleable(ptdnn_bert)

        # Engineered feature names test
        tr, cols = get_bert_in_datatransformer()
        name_last = tr.get_engineered_feature_names()[-1]
        err_msg = "Pretrained DNN eng. features names are broken. Eg eng. feature name = {}".format(name_last)
        assert name_last == "_".join(cols) + '_StringConcatTransformer_TestPretrainedTextDNNTransformer_149', err_msg

        # Ensure that if the download fails an exception is raised
        ptdnn_bert = TextFeaturizers.pretrained_text_dnn(embeddings_name="bert-base-uncased",
                                                         can_run_on_cpu=True)
        ptdnn_bert.provider._embedding_info._file_name = "berty-werty"
        with self.assertRaises(Exception):
            ptdnn_bert.fit(X, y)

        # clean-up the created folders/files
        DATA_FOLDER_PATH = os.path.join(os.getcwd(), 'data')
        if os.path.exists(DATA_FOLDER_PATH):
            shutil.rmtree(DATA_FOLDER_PATH)

        BERT_FOLDER_PATH = os.path.join(os.getcwd(), 'bert-base-uncased')
        if os.path.exists(BERT_FOLDER_PATH):
            shutil.rmtree(BERT_FOLDER_PATH)

    @unittest.skip("XLNet only works with higher versions of pytorch,hence ignoring for now")
    @if_package_exists("test_PretrainedTextDNNTransformer", ["torch", "pytorch_transformers"])
    def test_xlnet_fit_transform_pickleable(self):
        # TODO: XLNET is broken for multi-gpu due to pytorch dependency issue.
        ptdnn_xlnet =\
            TextFeaturizers.pretrained_text_dnn(
                embeddings_name="xlnet-base-cased",
                can_run_on_cpu=True)
        X = np.array(["hello world", "the world is all that is the case",
                      "a Quick Brown fox blah blah"])
        y = np.array([0, 1, 0])

        # Used as a sklearn transformer in a Pipeline
        clf = Pipeline([('pre', ptdnn_xlnet),
                        ('clf', LogisticRegression(solver='lbfgs'))])
        clf.fit(X, y)
        y_preds = clf.predict(X)
        assert len(y_preds) == len(X)

        # Inspect output of fine-tuned xlnet directly
        X_transform = ptdnn_xlnet.transform(X)
        assert X_transform.shape == (3, 150), "Actual shape\
        is {}".format(X_transform.shape)

        # pickle
        check_pickleable(ptdnn_xlnet)

        # clean-up the created folders/files
        DATA_FOLDER_PATH = os.path.join(os.getcwd(), 'data')
        if os.path.exists(DATA_FOLDER_PATH):
            shutil.rmtree(DATA_FOLDER_PATH)

        XLNET_FOLDER_PATH = os.path.join(os.getcwd(), 'xlnet-base-cased')
        if os.path.exists(XLNET_FOLDER_PATH):
            shutil.rmtree(XLNET_FOLDER_PATH)

    # *** Below are Bert/xlnet training tests that should be run on a GPU ***

    @unittest.skip("Takes too long on a cpu")
    def test_bert_e2e(self):
        """
        Tests BERT end-to-end for single GPU, multi-GPU as well as on a CPU
        machine for default settings like 32 bit floating point precision,
        no-early-stopping
        """
        ptdnn = TextFeaturizers.pretrained_text_dnn(
            verbose=True,
            embeddings_name="bert-base-uncased",
            do_lower_case=True,
            is_lower_dim=True,
            eval_batch_size=32,
            num_train_epochs=3,
            can_run_on_cpu=True)
        train_test(ptdnn)

        # clean-up the created folders/files
        DATA_FOLDER_PATH = os.path.join(os.getcwd(), 'data')
        if os.path.exists(DATA_FOLDER_PATH):
            shutil.rmtree(DATA_FOLDER_PATH)

        BERT_FOLDER_PATH = os.path.join(os.getcwd(), 'bert-base-uncased')
        if os.path.exists(BERT_FOLDER_PATH):
            shutil.rmtree(BERT_FOLDER_PATH)

    @unittest.skip("Takes too long on a cpu")
    def xlnet_e2e_test(self):
        """
        Tests XLNet end-to-end for single GPU, multi-GPU as well as on a CPU
        machine for default settings like 32 bit floating point precision,
        no-early-stopping
        """
        ptdnn = TextFeaturizers.pretrained_text_dnn(
            verbose=False,
            embeddings_name="xlnet-base-cased",
            do_lower_case=True,
            is_lower_dim=True,
            eval_batch_size=32,
            num_train_epochs=3,
            can_run_on_cpu=True)
        train_test(ptdnn)

        # clean-up the created folders/files
        DATA_FOLDER_PATH = os.path.join(os.getcwd(), 'data')
        if os.path.exists(DATA_FOLDER_PATH):
            shutil.rmtree(DATA_FOLDER_PATH)

        XLNET_FOLDER_PATH = os.path.join(os.getcwd(), 'xlnet-base-cased')
        if os.path.exists(XLNET_FOLDER_PATH):
            shutil.rmtree(XLNET_FOLDER_PATH)

    @unittest.skip("Takes too long on a cpu")
    def bert_e2e_16bit_test(self):
        """
        Tests BERT end-to-end for single GPU, multi-GPU as well as on a CPU
        machine for for mixed floating point precision. Read more here:
        https://nvidia.github.io/apex/amp.html
        """
        ptdnn = TextFeaturizers.pretrained_text_dnn(
            verbose=False,
            embeddings_name="bert-base-uncased",
            do_lower_case=True,
            is_lower_dim=True,
            eval_batch_size=32,
            num_train_epochs=3,
            fp16=True,
            can_run_on_cpu=True)
        train_test(ptdnn)

        # clean-up the created folders/files
        DATA_FOLDER_PATH = os.path.join(os.getcwd(), 'data')
        if os.path.exists(DATA_FOLDER_PATH):
            shutil.rmtree(DATA_FOLDER_PATH)

        BERT_FOLDER_PATH = os.path.join(os.getcwd(), 'bert-base-uncased')
        if os.path.exists(BERT_FOLDER_PATH):
            shutil.rmtree(BERT_FOLDER_PATH)

    @unittest.skip("Takes too long on a cpu")
    def xlnet_e2e_16bit_test(self):
        """
        Tests XLNet end-to-end for single GPU, multi-GPU as well as on a CPU
        machine for mixed floating point precision. Read more here:
        https://nvidia.github.io/apex/amp.html
        """
        ptdnn = TextFeaturizers.pretrained_text_dnn(
            verbose=False,
            embeddings_name="xlnet-base-cased",
            do_lower_case=True,
            is_lower_dim=True,
            eval_batch_size=32,
            num_train_epochs=3,
            fp16=True,
            can_run_on_cpu=True)
        train_test(ptdnn)

        # clean-up the created folders/files
        DATA_FOLDER_PATH = os.path.join(os.getcwd(), 'data')
        if os.path.exists(DATA_FOLDER_PATH):
            shutil.rmtree(DATA_FOLDER_PATH)

        XLNET_FOLDER_PATH = os.path.join(os.getcwd(), 'xlnet-base-cased')
        if os.path.exists(XLNET_FOLDER_PATH):
            shutil.rmtree(XLNET_FOLDER_PATH)

    @unittest.skip("Takes too long on a cpu")
    def bert_e2e_16bit_early_stopping_test(self):
        """
        Tests BERT end-to-end for single GPU, multi-GPU as well as on a CPU
        machine for for mixed floating point precision, and with
        Early Stopping enabled.
        """
        ptdnn = TextFeaturizers.pretrained_text_dnn(
            verbose=False,
            embeddings_name="bert-base-uncased",
            do_lower_case=True,
            is_lower_dim=True,
            eval_batch_size=32,
            num_train_epochs=3,
            fp16=True,
            early_stopping=True,
            can_run_on_cpu=True)
        train_test(ptdnn)

        # clean-up the created folders/files
        DATA_FOLDER_PATH = os.path.join(os.getcwd(), 'data')
        if os.path.exists(DATA_FOLDER_PATH):
            shutil.rmtree(DATA_FOLDER_PATH)

        BERT_FOLDER_PATH = os.path.join(os.getcwd(), 'bert-base-uncased')
        if os.path.exists(BERT_FOLDER_PATH):
            shutil.rmtree(BERT_FOLDER_PATH)

    @unittest.skip("Takes too long on a cpu")
    def xlnet_e2e_16bit_early_stopping_test(self):
        """
        Tests XLNet end-to-end for single GPU, multi-GPU as well as on a CPU
        machine for mixed floating point precision, and with
        Early Stopping enabled.
        """
        ptdnn = TextFeaturizers.pretrained_text_dnn(
            verbose=False,
            embeddings_name="xlnet-base-cased",
            do_lower_case=True,
            is_lower_dim=True,
            eval_batch_size=32,
            num_train_epochs=3,
            fp16=True,
            early_stopping=True,
            can_run_on_cpu=True)
        train_test(ptdnn)

        # clean-up the created folders/files
        DATA_FOLDER_PATH = os.path.join(os.getcwd(), 'data')
        if os.path.exists(DATA_FOLDER_PATH):
            shutil.rmtree(DATA_FOLDER_PATH)

        XLNET_FOLDER_PATH = os.path.join(os.getcwd(), 'xlnet-base-cased')
        if os.path.exists(XLNET_FOLDER_PATH):
            shutil.rmtree(XLNET_FOLDER_PATH)

    @unittest.skip("Takes too long on a cpu")
    def bert_e2e_early_stopping_test(self):
        """
        Tests BERT end-to-end for single GPU, multi-GPU as well as on a CPU
        machine for default settings like 32 bit floating point precision,
        with Early Stopping enabled.
        """
        ptdnn = TextFeaturizers.pretrained_text_dnn(
            verbose=False,
            embeddings_name="bert-base-uncased",
            do_lower_case=True,
            is_lower_dim=True,
            eval_batch_size=32,
            num_train_epochs=3,
            early_stopping=True,
            can_run_on_cpu=True)
        train_test(ptdnn)

        # clean-up the created folders/files
        DATA_FOLDER_PATH = os.path.join(os.getcwd(), 'data')
        if os.path.exists(DATA_FOLDER_PATH):
            shutil.rmtree(DATA_FOLDER_PATH)

        BERT_FOLDER_PATH = os.path.join(os.getcwd(), 'bert-base-uncased')
        if os.path.exists(BERT_FOLDER_PATH):
            shutil.rmtree(BERT_FOLDER_PATH)

    @unittest.skip("Takes too long on a cpu")
    def xlnet_e2e_early_stopping_test(self):
        """
        Tests XLNet end-to-end for single GPU, multi-GPU as well as on a CPU
        machine for default settings like 32 bit floating point precision,
        with Early Stopping enabled.
        """
        ptdnn = TextFeaturizers.pretrained_text_dnn(
            verbose=False,
            embeddings_name="xlnet-base-cased",
            do_lower_case=True,
            is_lower_dim=True,
            eval_batch_size=32,
            num_train_epochs=3,
            early_stopping=True,
            can_run_on_cpu=True)
        train_test(ptdnn)

        # clean-up the created folders/files
        DATA_FOLDER_PATH = os.path.join(os.getcwd(), 'data')
        if os.path.exists(DATA_FOLDER_PATH):
            shutil.rmtree(DATA_FOLDER_PATH)

        XLNET_FOLDER_PATH = os.path.join(os.getcwd(), 'xlnet-base-cased')
        if os.path.exists(XLNET_FOLDER_PATH):
            shutil.rmtree(XLNET_FOLDER_PATH)

    @unittest.skip("Takes too long on a cpu")
    def bert_e2e_infer1GPU_test(self):
        """
        Tests BERT end-to-end for single GPU, multi-GPU as well as on a CPU
        machine for default settings like 32 bit floating point precision,
        no-early-stopping
        """
        ptdnn = TextFeaturizers.pretrained_text_dnn(
            verbose=False,
            embeddings_name="bert-base-uncased",
            do_lower_case=True,
            is_lower_dim=True,
            eval_batch_size=32,
            num_train_epochs=3,
            can_run_on_cpu=True)
        train_test_infer1GPU(ptdnn)

        # clean-up the created folders/files
        DATA_FOLDER_PATH = os.path.join(os.getcwd(), 'data')
        if os.path.exists(DATA_FOLDER_PATH):
            shutil.rmtree(DATA_FOLDER_PATH)

        BERT_FOLDER_PATH = os.path.join(os.getcwd(), 'bert-base-uncased')
        if os.path.exists(BERT_FOLDER_PATH):
            shutil.rmtree(BERT_FOLDER_PATH)

    @unittest.skip("Takes too long on a cpu")
    def xlnet_e2e_infer1GPU_test(self):
        """
        Tests XLNet end-to-end for single GPU, multi-GPU as well as on a CPU
        machine for default settings like 32 bit floating point precision,
        no-early-stopping
        """
        ptdnn = TextFeaturizers.pretrained_text_dnn(
            verbose=False,
            embeddings_name="xlnet-base-cased",
            do_lower_case=True,
            is_lower_dim=True,
            eval_batch_size=32,
            num_train_epochs=3,
            can_run_on_cpu=True)
        train_test_infer1GPU(ptdnn)

        # clean-up the created folders/files
        DATA_FOLDER_PATH = os.path.join(os.getcwd(), 'data')
        if os.path.exists(DATA_FOLDER_PATH):
            shutil.rmtree(DATA_FOLDER_PATH)

        XLNET_FOLDER_PATH = os.path.join(os.getcwd(), 'xlnet-base-cased')
        if os.path.exists(XLNET_FOLDER_PATH):
            shutil.rmtree(XLNET_FOLDER_PATH)


if __name__ == "__main__":
    unittest.main()
