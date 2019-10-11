from unittest import TestCase

from zaach.math import prod


class ProdTests(TestCase):
    def test_prod_1_to_6(self):
        iterable = [1, 2, 3, 4, 5, 6]
        self.assertEqual(prod(iterable), 720)

    def test_prod_empty_iterable_raises_typeerror(self):
        with self.assertRaises(TypeError):
            prod([])

    def test_prod_non_digit_iterable_raises_typeerror(self):
        with self.assertRaises(TypeError):
            prod(["a", "b"])
