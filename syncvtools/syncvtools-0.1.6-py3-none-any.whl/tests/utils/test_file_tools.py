import unittest, tempfile
from syncvtools.utils.file_tools import _mpath
from syncvtools.utils.file_tools import *


class TestFileTools(unittest.TestCase):
    def test_json_read_to_object(self):
        json_obj = json_read_to_object(input_file=_mpath('syncvtools/examples/resources/prod_predictions/annotations/SP-200H-231_20190919_00000260_top.json'))
        self.assertTrue(isinstance(json_obj[0]['inferences'][0]['bounding_box']['xmin'],int))

    def test_get_file_list_by_ext(self):
        self.assertGreater(len(get_file_list_by_ext(dir=_mpath('syncvtools/examples/resources/pascalvoc/imgs/'),
                                         ext=('jpg','png','jpeg'),
                                         recursive=False)), 0)

        self.assertEqual(len(get_file_list_by_ext(dir=_mpath('syncvtools/examples/resources/'),
                                                 ext=('jpg', 'png', 'jpeg'),
                                                 recursive=False)), 0)
        self.assertGreater(len(get_file_list_by_ext(dir=_mpath('syncvtools/examples/resources/'),
                                                 ext=('jpg', 'png', 'jpeg'),
                                                 recursive=True)), 0)

    def test_cut_extension(self):
        self.assertEqual(cut_extension('test.jpeg'), 'test')
        self.assertEqual(cut_extension('test.test_ext', long_extensions=('test_ext',)), 'test')

    def test_dataset_filename_to_key(self):
        self.assertEqual(dataset_filename_to_key('/home/path/test.jpeg'), 'test')
        self.assertEqual(dataset_filename_to_key('test.img.239058'), 'test.img.239058')

    def test_pbmap_read_to_dict(self):
        f = pbmap_read_to_dict(input_file=_mpath('syncvtools/examples/resources/pascalvoc/label_map.ptxt'))
        self.assertGreater(len(f), 0)
        self.assertTrue(isinstance(list(f.keys())[0], int))

    def test_parse_xml_pascalvoc(self):
        f = parse_xml_pascalvoc(xml_path=_mpath('syncvtools/examples/resources/pascalvoc/annotations/100112-F-3091M-004.xml'))
        self.assertIsNotNone(f['annotation']['object'][0]['bndbox']['xmin'])


if __name__ == '__main__':
    print(__file__)
    unittest.main()