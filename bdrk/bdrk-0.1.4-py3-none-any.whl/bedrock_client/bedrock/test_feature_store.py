from typing import Any, List, Tuple

import pytest

import pandas as pd
from bedrock_client.bedrock.feature_store import FeatureStore, get_feature_store

TABLE = "TEST_TABLE"


@pytest.fixture
def schema() -> List[str]:
    return ["col1", "col2", "col3"]


@pytest.fixture
def feature(features) -> Tuple[str, Any]:
    return features[0]


@pytest.fixture
def features() -> List[Tuple[str, Any]]:
    return [
        ("key1", ("val1", "val2", "val3")),
        ("key2", ("val4", "val5", "val6")),
        ("key3", ("val7", "val8", "val9")),
    ]


@pytest.fixture
def fs() -> FeatureStore:
    return get_feature_store(mock_feature_store=True)


@pytest.fixture
def fs_with_schema(schema) -> FeatureStore:
    fs = get_feature_store(mock_feature_store=True)
    fs.create_feature(TABLE, schema=schema)
    return fs


def test_write(fs, features):
    fs.write(TABLE, features, batch_size=2)
    for feature_tuple in features:
        output = fs.read(TABLE, [feature_tuple[0]])
        expected = {feature_tuple[0]: feature_tuple[1]}
        assert output == expected, f"{str(output)}, {str(expected)}"


def test_read_with_schema(fs_with_schema, features, schema):
    fs_with_schema.write(TABLE, features)
    keys = list(map(lambda x: x[0], features))
    values = list(map(lambda x: dict(zip(schema, x[1])), features))
    expected = dict(zip(keys, values))
    output = fs_with_schema.read(TABLE, keys)
    assert output == expected, f"{str(output)}, {str(expected)}"


def test_read_no_schema(fs, features):
    fs.write(TABLE, features)
    keys = list(map(lambda x: x[0], features))
    values = list(map(lambda x: x[1], features))
    expected = dict(zip(keys, values))
    output = fs.read(TABLE, keys)
    assert output == expected, f"{str(output)}, {str(expected)}"


def test_write_pandas_df(fs):
    # Feature 'First'
    data = {
        "Name": ["Bob", "Alice", "Carol", "Ted"],
        "Age": [20, 21, 19, 18],
        "Sex": ["M", "F", "F", "M"],
        "ID": [231, 432, 112, 653],
    }
    df = pd.DataFrame(data)
    fs.write_pandas_df(df, "First", "Name", 2)

    keys = ["Bob", "Carol"]
    values = filter(lambda x: x["Name"] in keys, df.to_dict("records"))
    expected = dict(zip(keys, values))

    output = fs.read("First", keys)
    assert output == expected, f"{str(output)}, {str(expected)}"

    # Feature 'Second'
    data = {
        "Name": ["Bob", "Alice", "Carol", "Ted"],
        "Age": [20, 21, 19, 18],
        "Sex": ["M", "F", "F", "M"],
        "ID": [-231, -432, -112, -653],
    }
    df = pd.DataFrame(data)
    fs.write_pandas_df(df, "Second", "Name", 2)

    keys = ["Alice", "Carol"]
    values = filter(lambda x: x["Name"] in keys, df.to_dict("records"))
    expected = dict(zip(keys, values))

    output = fs.read("Second", keys)
    assert output == expected, f"{str(output)}, {str(expected)}"
