from django.test import TestCase

from kaf_pas.kd.models.documents import Documents
from kaf_pas.kd.models.pathes import Pathes


class Test_TestPathes(TestCase):
    def setUp(self):
        ...

    def test_1(self):
        Documents.objects.create()
        document = Documents.objects.filter(id=1).update(props=Documents.props.relevant)
        print(document)

    def test_2(self):
        self.path = "/path/path1/path2"
        TestPathes_item = Pathes.objects.create_ex(path=self.path, user=self.user, with_out_last=False)
        TestPathes_item = Pathes.objects.get(pk=TestPathes_item.id)
        self.assertEquals(TestPathes_item.absolute_path, self.path)

        self.path1 = 'E:/KAF/Кузова/К4310/К4310/К4310-232 Саратов, Радиан/К4310-232.50.00.000 - Кузов в сборе/К4310-232.52.00.000 - Выгородка/К4310-232.52.11.000 - Панель/К4310-232.52.11.000 - Панель.cdw'
        TestPathes_item = Pathes.objects.create_ex(path=self.path1, user=self.user, with_out_last=True)
        TestPathes_item = Pathes.objects.get(pk=TestPathes_item.id)
        self.assertEquals(TestPathes_item.absolute_path, '/KAF/Кузова/К4310/К4310/К4310-232 Саратов, Радиан/К4310-232.50.00.000 - Кузов в сборе/К4310-232.52.00.000 - Выгородка/К4310-232.52.11.000 - Панель')
