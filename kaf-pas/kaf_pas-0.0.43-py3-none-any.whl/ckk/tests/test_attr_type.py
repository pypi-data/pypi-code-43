from django.db import IntegrityError
from django.test import TestCase

from isc_common.auth.models.user import User
from isc_common.models.audit import IsBlankStr, NotUnique

from kaf_pas.ckk.models.attr_type import Attr_type


class Test_Attr_type(TestCase):
    def setUp(self):
        self.code = "code"
        self.name = "name"
        self.description = "parent"

    def test_1(self):
        attr_type = Attr_type.objects.create(code=self.code, name=self.name, description= self.description)
        attr_type = Attr_type.objects.get(pk=attr_type.id)
        self.assertEquals(attr_type.code, self.code)
        self.assertEquals(attr_type.name, self.name)
        self.assertEquals(attr_type.description, self.description)
        self.assertEquals(attr_type.parent, None)

        attr_type1 = attr_type
        self.code += "1"
        attr_type = Attr_type.objects.create(code=self.code, name=self.name, parent=attr_type1)
        attr_type = Attr_type.objects.get(pk=attr_type.id)
        self.assertEquals(attr_type.description, None)
        self.assertEquals(attr_type.name, self.name)
        self.assertEquals(attr_type.parent, attr_type1)

    def test_2(self):
        # with self.assertRaises(IntegrityError):
        Attr_type.objects.create(code=self.code, name=self.name)
        with self.assertRaises(IntegrityError):
            Attr_type.objects.create(name=self.name)

    def test_4(self):
        Attr_type.objects.create(code=self.code, name=self.name)
        with self.assertRaises(IntegrityError):
            Attr_type.objects.create(code=self.code, name=self.name)

    def tets_column_types(self):
        attr = Attr_type.objects.get_attr('SPC_CLM_FORMAT')
        self.assertEquals(attr.id, 4)
        attr = Attr_type.objects.get_attr('SPC_CLM_ZONE')
        self.assertEquals(attr.id, 5)
        attr = Attr_type.objects.get_attr('SPC_CLM_POS')
        self.assertEquals(attr.id, 6)
        attr = Attr_type.objects.get_attr('SPC_CLM_MARK')
        self.assertEquals(attr.id, 7)
        attr = Attr_type.objects.get_attr('SPC_CLM_NAME')
        self.assertEquals(attr.id, 8)
        attr = Attr_type.objects.get_attr('SPC_CLM_COUNT')
        self.assertEquals(attr.id, 9)
        attr = Attr_type.objects.get_attr('SPC_CLM_NOTE')
        self.assertEquals(attr.id, 10)
        attr = Attr_type.objects.get_attr('SPC_CLM_MASSA')
        self.assertEquals(attr.id, 11)
        attr = Attr_type.objects.get_attr('SPC_CLM_MATERIAL')
        self.assertEquals(attr.id, 12)
        attr = Attr_type.objects.get_attr('SPC_CLM_USER')
        self.assertEquals(attr.id, 13)
        attr = Attr_type.objects.get_attr('SPC_CLM_KOD')
        self.assertEquals(attr.id, 14)
        attr = Attr_type.objects.get_attr('SPC_CLM_FACTORY')
        self.assertEquals(attr.id, 15)
