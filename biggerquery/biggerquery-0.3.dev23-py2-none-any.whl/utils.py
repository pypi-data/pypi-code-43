import os
import gc
import zipfile
import tempfile
from unittest import TestCase
from unittest import main


def not_none_or_error(arg_value, arg_name):
    if arg_value is None:
        raise ValueError("{} can't be None".format(arg_name))


def secure_create_dataflow_manager_import():
    try:
        from .beam_manager import create_dataflow_manager
        return create_dataflow_manager
    except ImportError:
        return lambda *args, **kwargs: None


class AutoDeletedTmpFile(object):
    def __init__(self, tmp_file):
        self.tmp_file = tmp_file

    @property
    def name(self):
        return self.tmp_file.name

    def __del__(self):
        os.remove(self.tmp_file.name)


def unzip_file_and_save_outside_zip_as_tmp_file(file_path, suffix=''):
    path_parts = file_path.split(os.sep)
    zip_part_index = path_parts.index(next(p for p in path_parts if '.zip' in p))
    zip_path = os.path.join(os.sep, *path_parts[:zip_part_index + 1])
    with zipfile.ZipFile(zip_path, 'r') as zf:
        file_inside_zip_path = os.path.join(
            *[p if '.zip' not in p else p.split('.')[0] for p in path_parts][zip_part_index+1:])
        with zf.open(file_inside_zip_path) as file_inside_zip:
            tmp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
            content = file_inside_zip.read()
            tmp_file.write(content)
            tmp_file.close()
    return AutoDeletedTmpFile(tmp_file)


class UnzipFileAndSaveOutsideZipAsTmpFileTestCase(TestCase):

    def test_should_return_unzipped_autodestructable_file(self):

        # given
        test_case_dir_path = tempfile.mkdtemp(prefix='test_case')
        zip_path = os.path.join(test_case_dir_path, 'test_case_zip.zip')
        expected_zipped_file_content, zipped_file_name = 'chi', 'test_zipped_file'
        file_path_to_put_into_zip = os.path.join(test_case_dir_path, zipped_file_name)
        with open(file_path_to_put_into_zip, 'w') as f:
            f.write(expected_zipped_file_content)

        with zipfile.ZipFile(zip_path, 'w') as test_zip:
            test_zip.write(file_path_to_put_into_zip, zipped_file_name)
        zipped_file_path = os.path.join(zip_path, zipped_file_name)

        # when
        unzipped_file = unzip_file_and_save_outside_zip_as_tmp_file(zipped_file_path)

        # then
        with open(unzipped_file.name) as f:
            self.assertEqual(f.read(), 'chi')

        # when
        unzipped_file_path = unzipped_file.name
        unzipped_file = None
        gc.collect()

        # then
        self.assertFalse(os.path.exists(unzipped_file_path))


if __name__ == '__main__':
    main()