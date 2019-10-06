# This file is part of Tryton.  The COPYRIGHT file at the top level of this
# repository contains the full copyright notices and license terms.
import unittest

from trytond.model import fields


class FieldDependsTestCase(unittest.TestCase):
    'Test Field Depends'

    def test_empty_depends(self):
        'Test depends are set if empty'

        class Model(object):
            @fields.depends('name')
            def dependant(self):
                pass
        record = Model()

        record.dependant()

        self.assertIsNone(record.name)

    def test_set_depends(self):
        'Test depends are not modified if set'

        class Model(object):
            @fields.depends('name')
            def dependant(self):
                pass
        record = Model()
        record.name = "Name"

        record.dependant()

        self.assertEqual(record.name, "Name")

    def test_parent(self):
        'Test _parent_ depends are set'

        class Model(object):
            @fields.depends('_parent_parent.name',
                '_parent_parent.description')
            def dependant(self):
                pass
        parent = Model()
        parent.description = "Description"
        record = Model()
        record.parent = parent

        record.dependant()

        self.assertIsNone(record.parent.name)
        self.assertEqual(record.parent.description, "Description")

    def test_nested_parent(self):
        'Test nested _parent_ depends are set'

        class Model(object):
            @fields.depends('_parent_parent.name',
                '_parent_parent.description',
                '_parent_parent._parent_parent.name',
                '_parent_parent._parent_parent.description',)
            def dependant(self):
                pass
        grantparent = Model()
        grantparent.description = "Description"
        parent = Model()
        parent.parent = grantparent
        record = Model()
        record.parent = parent

        record.dependant()

        self.assertIsNone(record.parent.name)
        self.assertIsNone(record.parent.description)
        self.assertIsNone(record.parent.parent.name)
        self.assertEqual(record.parent.parent.description, "Description")


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(FieldDependsTestCase)
