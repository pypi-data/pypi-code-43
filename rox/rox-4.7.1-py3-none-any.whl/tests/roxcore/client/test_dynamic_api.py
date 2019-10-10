import unittest

from rox.core.client.dynamic_api import DynamicApi
from rox.core.configuration.models.experiment_model import ExperimentModel
from rox.core.entities.flag import Flag
from rox.core.entities.flag_setter import FlagSetter
from rox.core.entities.variant import Variant
from rox.core.repositories.experiment_repository import ExperimentRepository
from rox.core.repositories.flag_repository import FlagRepository
from rox.core.roxx.parser import Parser


class DynamicApiTests(unittest.TestCase):
    def test_is_enabled(self):
        parser = Parser()
        flag_repo = FlagRepository()
        exp_repo = ExperimentRepository()
        flag_setter = FlagSetter(flag_repo, parser, exp_repo, None)
        dynamic_api = DynamicApi(flag_repo, EntitiesMockProvider())

        self.assertTrue(dynamic_api.is_enabled('default.newFlag', True))
        self.assertEqual(True, flag_repo.get_flag('default.newFlag').is_enabled(None))
        self.assertFalse(dynamic_api.is_enabled('default.newFlag', False))
        self.assertEqual(1, len(flag_repo.get_all_flags()))

        exp_repo.set_experiments([ExperimentModel('1', 'default.newFlag', 'and(true, true)', False, ['default.newFlag'], set(), 'stam')])
        flag_setter.set_experiments()

        self.assertTrue(dynamic_api.is_enabled('default.newFlag', False))

    def test_is_enabled_after_setup(self):
        parser = Parser()
        flag_repo = FlagRepository()
        exp_repo = ExperimentRepository()
        flag_setter = FlagSetter(flag_repo, parser, exp_repo, None)
        dynamic_api = DynamicApi(flag_repo, EntitiesMockProvider())

        exp_repo.set_experiments([ExperimentModel('1', 'default.newFlag', 'and(true, true)', False, ['default.newFlag'], set(), 'stam')])
        flag_setter.set_experiments()

        self.assertTrue(dynamic_api.is_enabled('default.newFlag', False))

    def test_get_value(self):
        parser = Parser()
        flag_repo = FlagRepository()
        exp_repo = ExperimentRepository()
        flag_setter = FlagSetter(flag_repo, parser, exp_repo, None)
        dynamic_api = DynamicApi(flag_repo, EntitiesMockProvider())

        self.assertEqual('A', dynamic_api.value('default.newVariant', 'A', ['A', 'B', 'C']))
        self.assertEqual('A', flag_repo.get_flag('default.newVariant').get_value())
        self.assertEqual('B', dynamic_api.value('default.newVariant', 'B', ['A', 'B', 'C']))
        self.assertEqual(1, len(flag_repo.get_all_flags()))

        exp_repo.set_experiments([ExperimentModel('1', 'default.newVariant', 'ifThen(true, "B", "A")', False, ['default.newVariant'], set(), 'stam')])
        flag_setter.set_experiments()

        self.assertEqual('B', dynamic_api.value('default.newVariant', 'A', ['A', 'B', 'C']))


class EntitiesMockProvider:
    def create_flag(self, default_value):
        return Flag(default_value)

    def create_variant(self, default_value, options):
        return Variant(default_value, options)