import os

import pytest

from azureml.studio.common.error import InvalidZipFileError
from azureml.studio.core.utils.strutils import generate_random_string
from azureml.studio.modulehost.handler.data_handler import ZipHandler


def test_invalid_zip_file_error(tmpdir):
    file_name = generate_random_string()
    full_path = os.path.join(tmpdir, file_name)
    with open(full_path, 'w') as f:
        f.write("illegal zip file")

    with pytest.raises(InvalidZipFileError, match='Given ZIP file is not in the correct format'):
        zip_file_wrapper = ZipHandler.handle_argument_string(full_path)
        zip_file_wrapper.extractall(target_dir=tmpdir)
