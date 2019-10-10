import pytest

from flywheel_cli.util import is_dicom_file, KeyWithOptions, str_to_filename


def test_is_dicom_file():
    assert is_dicom_file('test.dcm')
    assert is_dicom_file('test.DCM')
    assert is_dicom_file('test.dicom')
    assert is_dicom_file('test.DICOM')
    assert is_dicom_file('test.dcm.gz')
    assert is_dicom_file('test.DCM.GZ')
    assert is_dicom_file('test.dicom.gz')
    assert is_dicom_file('test.DICOM.GZ')
    assert is_dicom_file('/full/path/to/test.dcm')

    assert not is_dicom_file('')
    assert not is_dicom_file('/')
    assert not is_dicom_file('/test.txt')
    assert not is_dicom_file('/dcm.test')
    assert not is_dicom_file('test.dcmisnt')
    assert not is_dicom_file('test.dcm.zip')


def test_key_with_options():
    # Raises key error if key is missing
    with pytest.raises(KeyError):
        KeyWithOptions({})

    # String value
    opts = KeyWithOptions('value')
    assert opts.key == 'value'
    assert opts.config == {}

    # Other value types
    opts = KeyWithOptions(4.2)
    assert opts.key == 4.2
    assert opts.config == {}

    # Dictionary with options
    opts = KeyWithOptions({
        'name': 'Test Name',
        'option': 8.0
    })
    assert opts.key == 'Test Name'
    assert opts.config == {'option': 8.0}

    # Dictionary with key override
    opts = KeyWithOptions({
        'pattern': 'Test Pattern',
    }, key='pattern')
    assert opts.key == 'Test Pattern'
    assert opts.config == {}


def test_str_to_filename():
    assert str_to_filename('test ?_.dicom.zip') == 'test _.dicom.zip'
    assert str_to_filename('test ?/.dicom.zip') == 'test _.dicom.zip'
    assert str_to_filename('test-1?/**test.dicom.zip') == 'test-1_test.dicom.zip'
