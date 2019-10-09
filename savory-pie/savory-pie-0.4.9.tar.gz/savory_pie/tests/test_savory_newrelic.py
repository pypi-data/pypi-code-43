import unittest

from savory_pie.savory_newrelic import get_transaction_name_path


class SavoryPieNewRelicTestCase(unittest.TestCase):

    def _assertMakesInto(self, input, output):
        self.assertEqual(get_transaction_name_path(input), output)

    def _assertDoesNotChange(self, input):
        self._assertMakesInto(input, input)

    def test_does_not_modify_okay_paths(self):
        self._assertDoesNotChange('bars/magic8ball')

        self._assertDoesNotChange('merchandising')

        self._assertDoesNotChange('merchandising/productcontext')

        self._assertDoesNotChange('merchandising/productcontext/')

        self._assertDoesNotChange('merchandising/productcontext/magic99')

    def test_removes_final_id_from_resource_paths(self):
        self._assertMakesInto('bars/foo', 'bars/foo')
        self._assertMakesInto('bars/bar/9', 'bars/bar')
        self._assertMakesInto('bars/19229', 'bars')

        self._assertMakesInto(
            'merchandising/productcontext/493949',
            'merchandising/productcontext'
        )

        self._assertMakesInto(
            'merchandising/productcontext/awesomeness/493949',
            'merchandising/productcontext/awesomeness'
        )
