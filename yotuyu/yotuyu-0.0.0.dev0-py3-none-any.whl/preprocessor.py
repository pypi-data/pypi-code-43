from sklearn.model_selection import train_test_split

from yotuyu.loader import __load_sample_data


def df_to_dataset(df):
    target = df['target'].to_numpy()
    df = df.drop(columns='target')
    data = df.to_numpy()
    return data, target


def split(dataset, ratio):
    data, target = dataset
    train_data, test_data, train_target, test_target = train_test_split(data, target, test_size=ratio)
    return train_data, train_target, test_data, test_target


if __name__ == '__main__':
    from pathlib import Path

    sample_file = Path.cwd() / Path('../data/sample.csv')

    _ds = __load_sample_data(sample_file)
    _target = _ds['target'].to_numpy()
    _ds = _ds.drop(columns='target')

    _data = _ds.to_numpy()
    print(_data.shape)
