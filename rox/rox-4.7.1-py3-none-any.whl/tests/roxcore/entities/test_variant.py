import unittest

from rox.core.configuration.models.experiment_model import ExperimentModel
from rox.core.entities.variant import Variant
from rox.core.impression.impression_invoker import ImpressionInvoker
from rox.core.roxx.evaluation_result import EvaluationResult

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class VariantTests(unittest.TestCase):
    def test_will_not_add_default_to_options_if_exists(self):
        variant = Variant('1', ['1', '2', '3'])
        self.assertEqual(3, len(variant.options))

    def test_will_add_default_to_options_if_not_exists(self):
        variant = Variant('1', ['2', '3'])

        self.assertEqual(3, len(variant.options))
        self.assertTrue('1' in variant.options)

    def test_will_set_name(self):
        variant = Variant('1', ['2', '3'])

        self.assertIsNone(variant.name)

        variant.set_name('bop')

        self.assertEqual('bop', variant.name)

    def test_will_return_default_value_when_no_parser_or_condition(self):
        variant = Variant('1', ['2', '3'])

        self.assertEqual('1', variant.get_value())

        parser = Mock()
        variant.set_for_evaluation(parser, None, None)

        self.assertEqual('1', variant.get_value())

        variant.set_for_evaluation(None, ExperimentModel('id', 'name', '123', False, ['1'], set(), 'stam'), None)

        self.assertEqual('1', variant.get_value())

    def test_will_return_default_value_when_result_not_in_options(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult('xxx')

        variant = Variant('1', ['2', '3'])
        variant.set_for_evaluation(parser, ExperimentModel('id', 'name', '123', False, ['1'], set(), 'stam'), None)

        self.assertEqual('xxx', variant.get_value())

    def test_will_return_value_when_on_evaluation(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult('2')

        variant = Variant('1', ['2', '3'])
        variant.set_for_evaluation(parser, ExperimentModel('id', 'name', '123', False, ['1'], set(), 'stam'), None)

        self.assertEqual('2', variant.get_value())

    def test_will_raise_impression(self):
        parser = Mock()
        parser.evaluate_expression.return_value = EvaluationResult('2')

        is_impression_raised = {'raised': False}

        def on_impression(e):
            is_impression_raised['raised'] = True

        internal_flags = Mock()
        imp_invoker = ImpressionInvoker(internal_flags, None, None, None, None)
        imp_invoker.register_impression_handler(on_impression)

        variant = Variant('1', ['2', '3'])
        variant.set_for_evaluation(parser, ExperimentModel('id', 'name', '123', False, ['1'], set(), 'stam'), imp_invoker)

        self.assertEqual('2', variant.get_value())
        self.assertTrue(is_impression_raised['raised'])
