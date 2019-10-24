from unittest import TestCase, mock
from k9.pretty_object import PrettyObject, get_tag, get_tags, get_name, get_true
import io

class TestPrettyObject(TestCase):

    def test_get_tags(self):
        tags = [{"Key": "Name", "Value": "default-vpc"}, {"Key": "Author", "Value": "simon.woo"}]
        value = get_tags(tags)
        self.assertEqual("default-vpc", value["Name"] )
        self.assertEqual("simon.woo", value["Author"] )

    def test_get_tag(self):
        tags = [{"Key": "Name", "Value": "default-vpc"}]
        value = get_tag(tags, "Name")
        self.assertEqual( "default-vpc", value )

    def test_get_name(self):
        tags = [{"Key": "Name", "Value": "default-vpc"}]
        value = get_name(tags)
        self.assertEqual("default-vpc", value)
        value = get_name([])
        self.assertEqual('', value)

    def test_get_true(self):
        value = get_true(True)
        self.assertEqual('True', value)
        value = get_true(False)
        self.assertEqual('', value)

    def test_pretty_dictionary(self):
        po = PrettyObject()
        obj = {"test": "test", "test2": "test2"}
        result = po.string(obj)
        self.assertEqual('{\n'
                         '    test: "test"\n'
                         '    test2: "test2"\n'
                         '}', result)

        obj = {"test": [], "test2": "test2"}
        result = po.string(obj)
        self.assertEqual('{\n'
                         '    test: []\n'
                         '    test2: "test2"\n'
                         '}', result)

        obj = {"test": {"test": "test"}}
        result = po.string(obj)
        self.assertEqual('{\n'
                         '    test: {\n'
                         '        test: "test"\n'
                         '    }\n'
                         '}', result)

        obj = {"test": {"test": "test", "test2": {"test3": "test3"}}}
        result = po.string(obj)
        self.assertEqual('{\n'
                         '    test: {\n'
                         '        test: "test"\n'
                         '        test2: {\n'
                         '            test3: "test3"\n'
                         '        }\n'
                         '    }\n'
                         '}', result)

    def test_pretty_dictionary_line(self):
        po = PrettyObject()
        po.dictLimit = 10
        obj = {"test": "test", "test2": "test2"}
        result = po.string(obj)
        self.assertEqual('{test: "test", test2: "test2"}', result)

        obj = {"test": {"test": "test"}}
        result = po.string(obj)
        self.assertEqual('{test: {test: "test"}}', result)

        obj = {"test": {"test": "test", "test2": {"test3": "test3"}}}
        result = po.string(obj)
        self.assertEqual('{test: {test: "test", test2: {test3: "test3"}}}', result)

    def test_pretty_list(self):
        po = PrettyObject()

        obj = ["test1", "test2"]
        result = po.string(obj)
        self.assertEqual('[\n'
                         '    "test1"\n'
                         '    "test2"\n'
                         ']', result)

        obj = ["test1", {"test": "test2"}]
        result = po.string(obj)
        self.assertEqual('[\n'
                         '    "test1"\n'
                         '    {\n'
                         '        test: "test2"\n'
                         '    }\n'
                         ']', result)

    def test_pretty_list_line(self):
        po = PrettyObject()
        po.dictLimit = 10
        po.listLimit = 10
        obj = ["test1", "test2"]
        result = po.string(obj)
        self.assertEqual('["test1", "test2"]', result)

        obj = ["test1", {"test": "test"}]
        result = po.string(obj)
        self.assertEqual('["test1", {test: "test"}]', result)

    def test_pretty_tuple(self):
        po = PrettyObject()

        obj = ("test1", "test2")
        result = po.string(obj)
        self.assertEqual('(\n'
                         '    "test1"\n'
                         '    "test2"\n'
                         ')', result)

        obj = ("test1", {"test": "test2"})
        result = po.string(obj)
        self.assertEqual('(\n'
                         '    "test1"\n'
                         '    {\n'
                         '        test: "test2"\n'
                         '    }\n'
                         ')', result)

    def test_pretty_tuple_line(self):
        po = PrettyObject()
        po.dictLimit = 10
        po.listLimit = 10
        obj = ("test1", "test2")
        result = po.string(obj)
        self.assertEqual('("test1", "test2")', result)

        obj = ("test1", {"test": "test"})
        result = po.string(obj)
        self.assertEqual('("test1", {test: "test"})', result)

    @mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print(self, mock_stdout):
        po = PrettyObject()

        obj = [
            {"Name": "default-vpc", "VpcId": "vpc-2eb67c54", "CidrBlock": "172.31.0.0/16", "IsDefault": True, "State": "available"},
            {"Name": "dvl-vpc", "VpcId": "vpc-422314113412", "CidrBlock": "10.0.0.0/16", "IsDefault": False, "State": "pending"}
        ]
        po.print(obj)
        self.assertTrue('vpc-2eb67c54' in mock_stdout.getvalue())
        self.assertTrue('vpc-422314113412' in mock_stdout.getvalue())

    @mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_table(self, mock_stdout):
        po = PrettyObject()

        obj = [
            {"Name": "default-vpc", "VpcId": "vpc-2eb67c54", "CidrBlock": "172.31.0.0/16", "IsDefault": True, "State": "available"},
            {"Name": "dvl-vpc", "VpcId": "vpc-422314113412", "CidrBlock": "10.0.0.0/16", "IsDefault": False, "State": "pending"}
        ]
        po.print_table(obj)
        self.assertTrue('vpc-2eb67c54' in mock_stdout.getvalue())
        self.assertTrue('vpc-422314113412' in mock_stdout.getvalue())
