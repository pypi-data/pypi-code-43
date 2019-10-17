import os
import pickle
import pandas as pd

from azureml.studio.core.io.any_directory import AnyDirectory
from azureml.studio.core.io.model_directory import save_model_to_directory, ModelDirectory
from azureml.studio.core.io.model_directory import pickle_dumper, pickle_loader
from azureml.studio.core.io.data_frame_directory import save_data_frame_to_directory, DataFrameDirectory
from azureml.studio.common.io.transform_directory import save_transform_to_directory, TransformDirectory
from azureml.studio.common.io.directory_loader import load_from_directory


def test_load_from_directory_data_frame(tmp_path):
    df = pd.DataFrame({'col1': [1.0, 2.0, 3.3], 'col2': [1e9, 1e19, 1e29]})
    save_data_frame_to_directory(tmp_path, data=df)
    dir_data = load_from_directory(tmp_path)
    assert dir_data.type == DataFrameDirectory.TYPE_NAME
    assert df.equals(dir_data.data)


def test_load_from_directory_model(tmp_path):
    model = {'str': 'bbb', 'int': 123, 'list': [1, 2, 3], 'dict': {'key': 'val'}}
    dumper = pickle_dumper(model)
    save_model_to_directory(tmp_path, model_dumper=dumper)
    dir_data = load_from_directory(tmp_path, model_loader=pickle_loader)
    assert dir_data.type == ModelDirectory.TYPE_NAME
    assert model == dir_data.data


def test_load_from_directory_any(tmp_path):
    AnyDirectory.create().dump(tmp_path)
    dir_data = load_from_directory(tmp_path)
    assert dir_data.type == AnyDirectory.TYPE_NAME


def test_load_from_directory_transform(tmp_path):
    path = 'transform.pkl'
    transform = {'str': 'bbb', 'int': 123, 'list': [1, 2, 3], 'dict': {'key': 'val'}}
    full_path = os.path.join(tmp_path, path)
    with open(full_path, 'wb') as fout:
        pickle.dump(transform, fout)
    save_transform_to_directory(tmp_path, path)
    directory = load_from_directory(tmp_path)
    assert directory.type == TransformDirectory.TYPE_NAME
    assert directory.data == transform
