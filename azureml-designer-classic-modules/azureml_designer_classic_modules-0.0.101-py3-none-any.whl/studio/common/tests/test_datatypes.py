import pytest

from azureml.studio.common.datatypes import DataTypes


def test_load_from_file_name():
    assert DataTypes.from_file_name('data.csv') == DataTypes.GENERIC_CSV
    assert DataTypes.from_file_name('data.tsv') == DataTypes.GENERIC_TSV
    assert DataTypes.from_file_name('data.nh.csv') == DataTypes.GENERIC_CSV_NO_HEADER
    assert DataTypes.from_file_name('data.nh.tsv') == DataTypes.GENERIC_TSV_NO_HEADER
    assert DataTypes.from_file_name('data.txt') == DataTypes.PLAIN_TEXT
    assert DataTypes.from_file_name('data.bin') == DataTypes.GENERIC_BINARY
    assert DataTypes.from_file_name('data.htm') == DataTypes.GENERIC_HTML
    assert DataTypes.from_file_name('data.net') == DataTypes.GENERIC_DOT_NET
    assert DataTypes.from_file_name('data.datatable') == DataTypes.DATATABLE_DOT_NET
    assert DataTypes.from_file_name('data.dataset.parquet') == DataTypes.DATASET


def test_load_from_file_name_with_invalid_secondary_extension():
    assert DataTypes.from_file_name('data.unknown.csv') == DataTypes.GENERIC_CSV
    assert DataTypes.from_file_name('data.unknown.tsv') == DataTypes.GENERIC_TSV


def test_load_from_file_name_with_path():
    assert DataTypes.from_file_name('/data.csv') == DataTypes.GENERIC_CSV
    assert DataTypes.from_file_name('/path/to/data.tsv') == DataTypes.GENERIC_TSV
    assert DataTypes.from_file_name('C:\\path\\to\\data.nh.csv') == DataTypes.GENERIC_CSV_NO_HEADER
    assert DataTypes.from_file_name('C:\\data.nh.tsv') == DataTypes.GENERIC_TSV_NO_HEADER


def test_load_from_file_name_with_bad_extensions():
    with pytest.raises(ValueError, match="Unable to detect DataType: Unrecognized file extension '.unknown'."):
        DataTypes.from_file_name('data.unknown')

    with pytest.raises(ValueError, match="Unable to detect DataType: No file extension."):
        DataTypes.from_file_name('data')


@pytest.mark.parametrize(
    'file_name, expected_datatype', [
        ('input0.ilearner', DataTypes.LEARNER),
        ('input0.data.ilearner', DataTypes.LEARNER),
        ('input0.alghost.ilearner', DataTypes.LEARNER),
        ('input0.nh.ilearner', DataTypes.LEARNER),
        ('data.dataset.parquet', DataTypes.DATASET),
        ('data.csv.dataset.parquet', DataTypes.DATASET),
        ('alghost.csv', DataTypes.GENERIC_CSV),
        ('alghost.dataset.csv', DataTypes.GENERIC_CSV),
        ('alghost.dataset.nh.csv', DataTypes.GENERIC_CSV_NO_HEADER)
    ]
)
def test_from_file_name(file_name, expected_datatype):
    computed_datatype = DataTypes.from_file_name(file_name)
    assert computed_datatype == expected_datatype
