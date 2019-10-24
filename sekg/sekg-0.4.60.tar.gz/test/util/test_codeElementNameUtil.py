from unittest import TestCase

from sekg.util.code import CodeElementNameUtil


class TestCodeElementNameUtil(TestCase):
    def test_uncamelize(self):
        util = CodeElementNameUtil()
        name_list = [
            ("java.util.List", "java.util. List"),
            ("java.util.ArrayList", "java.util. Array List"),
            ("ArrayList", "Array List"),
            ("FPath1", "F Path1"),
            ("FilePath1", "File Path1"),
            ("Word2Vec", "Word2Vec"),
            ("arrayList", "array List"),
            ("HTML5", "HTML5"),
            ("0xB8CFE5","0xB8CFE5"),
            ("AWT's threading model", "AWT's threading model"),
            ("32-bit integer","32-bit integer")

        ]
        for name, right_name in name_list:
            print(right_name, util.uncamelize(name))
            # self.assertEqual(right_name, util.uncamelize(name))

    def test_uncamelize_by_stemming(self):
        util = CodeElementNameUtil()
        name_list = [
            ("java.util.List", "java.util. List"),
            ("java.util.ArrayList", "java.util. Array List"),
            ("ArrayList", "Array List"),
            ("FPath1", "F Path1"),
            ("FilePath1", "File Path1"),
            ("HTML5", "HTML5"),
            ("word2vec", "word2vec"),
            ("Word2Vec", "Word2Vec"),
            ("Word2Vec2", "Word2Vec"),
            ("3D", "3D"),
            ("three TreePaths", "three Tree Paths"),
            ("0xB8CFE5","0xB8CFE5"),
            ("AWT 's threading model","AWT 's threading model"),
            ("32-bit integer", "32-bit integer"),
        ]
        for name, right_name in name_list:
            print(right_name, util.uncamelize_by_stemming(name))
            #self.assertEqual(right_name, util.uncamelize_by_stemming(name))

    def test_uncamelize_from_simple_name(self):
        util = CodeElementNameUtil()
        name_list = [
            ("java.util.List", "List"),
            ("java.util.ArrayList", "Array List"),
            ("ArrayList", "Array List"),
            ("FPath1", "F Path1"),
            ("FilePath1", "File Path1"),
        ]
        for name, right_name in name_list:
            self.assertEqual(right_name, util.uncamelize_from_simple_name(name))

    def test_generate_aliases(self):
        util = CodeElementNameUtil()
        name_list = [
            "java.util.List",
            "java.util.ArrayList",
            "ArrayList",
            "FPath1",
            "FilePath1",
            "HTML5",
            "word2vec",
            "NEWARRAY",
            "AWT 's threading model"
        ]
        for name in name_list:
            print("ori: ", name)
            print("aliase:", util.generate_aliases(name))
