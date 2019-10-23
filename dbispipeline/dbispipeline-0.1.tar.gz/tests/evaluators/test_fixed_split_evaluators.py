# noqa: D100
import json
import unittest

from dbispipeline.evaluators import ClassificationEvaluator
from dbispipeline.evaluators import FixedSplitEvaluator
from dbispipeline.evaluators import FixedSplitGridEvaluator
from sklearn import metrics
from sklearn.multiclass import OneVsRestClassifier
from sklearn.neighbors import KNeighborsClassifier

from tests.dataloaders.dummy_loader import MockTrainTestLoader
from tests.evaluators.dummy_models import split_checking
from tests.evaluators.dummy_models import SplitCheckingModel


class TestFixedSplitEvaluator(unittest.TestCase):
    """Tests the FixedSplitEvaluator."""

    def test_scoring(self):
        """Tests if the scoring metrics are used correctly."""
        dataloader = MockTrainTestLoader(n_classes=4)
        data = dataloader.load()
        train, test = data
        model = OneVsRestClassifier(KNeighborsClassifier())
        evaluator = FixedSplitEvaluator(
            scoring={
                'f1_macro':
                metrics.get_scorer('f1_macro'),
                'roc_auc':
                metrics.make_scorer(
                    metrics.roc_auc_score, average='macro', needs_proba=True),
                'confusion_matrix':
                metrics.make_scorer(metrics.multilabel_confusion_matrix),
                'roc_auc_all':
                metrics.make_scorer(metrics.roc_auc_score, average=None),
            })

        result = evaluator.evaluate(model, data)

        self.assertCountEqual(
            result.keys(),
            ['f1_macro', 'roc_auc', 'confusion_matrix', 'roc_auc_all'],
        )

        f1_macro = metrics.get_scorer('f1_macro')
        roc_auc = metrics.get_scorer('roc_auc')
        self.assertEqual(result['f1_macro'], f1_macro(model, *test))
        self.assertEqual(result['roc_auc'], roc_auc(model, *test))
        self.assertIsInstance(json.dumps(result), str)

    def test_configuration(self):
        """Tests if the configuration is set and json serializable."""
        scoring = {
            'confusion_matrix':
            metrics.make_scorer(metrics.multilabel_confusion_matrix),
            'roc_auc_all':
            metrics.make_scorer(metrics.roc_auc_score, average=None),
        }

        evaluator = FixedSplitEvaluator(scoring=scoring)

        self.assertEqual(evaluator.configuration,
                         {'scoring': list(scoring.keys())})
        self.assertIsInstance(json.dumps(evaluator.configuration), str)

    def test_splitting(self):
        """Tests if the splits are kept the same."""
        dataloader = MockTrainTestLoader(n_features=5, n_classes=4)
        model = SplitCheckingModel(dataloader=dataloader)
        data = dataloader.load()
        train, test = data

        self.assertFalse(split_checking['train_correct'])
        self.assertFalse(split_checking['test_correct'])

        evaluator = FixedSplitEvaluator(
            scoring={
                'f1_macro':
                metrics.get_scorer('f1_macro'),
                'confusion_matrix':
                metrics.make_scorer(metrics.multilabel_confusion_matrix),
                'roc_auc_all':
                metrics.make_scorer(metrics.roc_auc_score, average=None),
            })
        evaluator.evaluate(model, dataloader.load())

        self.assertTrue(model.train_split_correct)
        self.assertTrue(model.test_split_correct)


class TestFixedSplitGridEvaluator(unittest.TestCase):
    """Tests the FixedSplitGridEvaluator."""

    def test_splitting(self):
        """Tests if the splits are kept the same."""
        dataloader = MockTrainTestLoader(n_features=5, n_classes=4)
        # test code is in the model
        model = SplitCheckingModel(dataloader=dataloader)

        self.assertFalse(split_checking['train_correct'])
        self.assertFalse(split_checking['test_correct'])

        evaluator = FixedSplitGridEvaluator(
            params={},
            grid_params={
                'verbose': 0,
                'refit': False,
            },
        )
        evaluator.evaluate(model, dataloader.load())

        self.assertTrue(split_checking['train_correct'])
        self.assertTrue(split_checking['test_correct'])


class TestClassificationEvaluator(unittest.TestCase):
    """Tests the ClassificationEvaluator."""

    def test_scoring(self):
        """Tests if the scoring metrics are used correctly."""
        dataloader = MockTrainTestLoader(n_classes=1)
        model = KNeighborsClassifier()
        evaluator = ClassificationEvaluator()

        result = evaluator.evaluate(model, dataloader.load())

        self.assertCountEqual(
            result.keys(),
            ['f1', 'accuracy', 'recall', 'precision', 'confusion_matrix'])

        self.assertEqual(len(result['confusion_matrix']), 2)
        self.assertIsInstance(json.dumps(result), str)

    def test_configuration(self):
        """Tests if the configuration is set and json serializable."""
        evaluator = ClassificationEvaluator(average='macro')

        config = {
            'average':
            'macro',
            'scoring':
            ['f1', 'accuracy', 'recall', 'precision', 'confusion_matrix'],
        }

        self.assertEqual(evaluator.configuration, config)
        self.assertIsInstance(json.dumps(evaluator.configuration), str)
