# -*- coding: utf-8 -*-
import tensorflow as tf
import tensorflow_datasets as tfds
import six
import csv
import collections
from six.moves import urllib
import pandas as pd
import numpy as np
from skydl.datasets.super_tf_dataset_builder import DefaultDatasetBuilderConfig, SuperDatasetBuilder
import os,sys
sys.path.append(os.path.abspath('%s/..' % sys.path[0]))

_LABEL_DICT = collections.OrderedDict([
    ("1", "1st_class"), ("2", "2nd_class"), ("3", "3rd_class"), ("4", "4rd_class"), ("5", "5rd_class")
])


class MovieLensDatasetBuilder(SuperDatasetBuilder):
    """
    参考 tensorflow-datasets/mnist.py
    https://github.com/tensorflow/models/blob/master/official/datasets/movielens.py
    """
    BUILDER_CONFIGS = [
        DefaultDatasetBuilderConfig(
            name="plain_text",
            version="0.0.15",
            description="Plain text",
        ),
        DefaultDatasetBuilderConfig(
            name="bytes",
            version="0.0.1",
            description=("Uses byte-level text encoding with "
                         "`tfds.features.text.ByteTextEncoder`"),
            text_encoder_config=tfds.features.text.TextEncoderConfig(
                encoder=tfds.features.text.ByteTextEncoder()),
        ),
        DefaultDatasetBuilderConfig(
            name="subwords8k",
            version="0.0.1",
            description=("Uses `tfds.features.text.SubwordTextEncoder` with 8k "
                         "vocab size"),
            text_encoder_config=tfds.features.text.TextEncoderConfig(
                encoder_cls=tfds.features.text.SubwordTextEncoder,
                vocab_size=2 ** 13),
        ),
        DefaultDatasetBuilderConfig(
            name="subwords32k",
            version="0.0.1",
            description=("Uses `tfds.features.text.SubwordTextEncoder` with "
                         "32k vocab size"),
            text_encoder_config=tfds.features.text.TextEncoderConfig(
                encoder_cls=tfds.features.text.SubwordTextEncoder,
                vocab_size=2 ** 15),
        ),
    ]

    RATINGS_FILE = "ratings"
    MOVIES_FILE = "movies"
    USERS_FILE = "users"
    JOINT_FILE = "joint"
    GENRE_COLUMN = "genres"
    ITEM_COLUMN = "item_id"  # movies
    RATING_COLUMN = "rating"
    TIMESTAMP_COLUMN = "timestamp"
    TITLE_COLUMN = "titles"
    USER_COLUMN = "user_id"
    GENRES = [
        'Action', 'Adventure', 'Animation', "Children's", 'Comedy', 'Crime',
        'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', "IMAX", 'Musical',
        'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
    ]
    GENRES_CATEGORICAL_FEATURE_COLUMN = SuperDatasetBuilder.build_one_hot_feature_column(SuperDatasetBuilder.build_categorical_column_with_vocabulary_list(
                                                                                "genres", GENRES))
    N_GENRE = len(GENRES)

    RATING_COLUMNS = [USER_COLUMN, ITEM_COLUMN, RATING_COLUMN, TIMESTAMP_COLUMN]
    MOVIE_COLUMNS = [ITEM_COLUMN, TITLE_COLUMN, GENRE_COLUMN]
    USER_COLUMNS = [USER_COLUMN, 'gender', 'age', 'occupation', 'zip']

    RATING_FEATURE_DICT = collections.OrderedDict([
        ("user_id", (tf.int32, SuperDatasetBuilder.convert_to_int)),
        ("gender", (tf.string, SuperDatasetBuilder.convert_to_string)),
        ("age", (tf.int32, SuperDatasetBuilder.convert_to_int)),
        ("occupation", (tf.int32, SuperDatasetBuilder.convert_to_int)),
        ("zip", (tf.string, SuperDatasetBuilder.convert_to_string)),
        ("item_id", (tf.int32, SuperDatasetBuilder.convert_to_int)),
        ("timestamp", (tf.int32, SuperDatasetBuilder.convert_to_int)),
        # ("genres", (tf.string, SuperDatasetBuilder.convert_to_string))
        ("genres", (tfds.features.Tensor(dtype=tf.int64, shape=(None,)), SuperDatasetBuilder.convert_to_int_from_string))  # genres是不定长的一维数组，e.g. [7] or [14,23,55]
    ])

    def __init__(self, data_dir=None, config=None):
        super().__init__(data_dir=data_dir, config=config)
        self._num_shards = 1
        self._train_data_file = "http://files.grouplens.org/datasets/movielens/"
        self._test_data_file = None
        self._validation_data_file = None

    def _info(self):
        return tfds.core.DatasetInfo(
            builder=self,
            description=("movielens dataset"),
            features=tfds.features.FeaturesDict({
                "label": tfds.features.ClassLabel(names=[label for label in _LABEL_DICT.values()]),
                "feature": {name: dtype
                            for name, (dtype, func) in self.RATING_FEATURE_DICT.items()},
            }),
            supervised_keys=("feature", "label"),
            urls=["https://xxx"],
            citation="@ONLINE {movielens dataset}"
        )

    def _split_generators(self, dl_manager):
        filenames = {
            "ml-1m": "ml-1m.zip",
        }
        generator_array = []
        if self._train_data_file:
            # added checksums file: tensorflow_datasets/url_checksums/movie_lens_dataset_builder.txt
            dl_manager._register_checksums = True
            data_files = dl_manager.download_and_extract(
                {k: urllib.parse.urljoin(self._train_data_file, v) for k, v in filenames.items()})
            generator_array.append(tfds.core.SplitGenerator(
                name=tfds.Split.TRAIN,
                num_shards=3,
                gen_kwargs={
                    "data_path": data_files['ml-1m']
                }))
        if self._test_data_file:
            generator_array.append(tfds.core.SplitGenerator(
                name=tfds.Split.TEST,
                num_shards=1,
                gen_kwargs={
                    "data_path": self._test_data_file
                }))
        if self._validation_data_file:
            generator_array.append(tfds.core.SplitGenerator(
                name=tfds.Split.VALIDATION,
                num_shards=1,
                gen_kwargs={
                    "data_path": self._validation_data_file
                }))
        return generator_array

    def _generate_examples(self, **kwargs):
        """Generate features and target given the directory path.
        Args:
          file_path: path where the csv file is stored
        Yields:
          The features and the target
        """
        data_path = kwargs.get("data_path")
        for dataset_path_name in tf.io.gfile.listdir(data_path):
            self._transform_csv(
                input_path=data_path + "/" + dataset_path_name + "/" + self.RATINGS_FILE + ".dat",
                output_path=data_path + "/" + dataset_path_name + "/" + self.RATINGS_FILE + ".csv",
                names=self.RATING_COLUMNS, skip_first=False, separator="::")
            self._transform_csv(
                input_path=data_path + "/" + dataset_path_name + "/" + self.MOVIES_FILE + ".dat",
                output_path=data_path + "/" + dataset_path_name + "/" + self.MOVIES_FILE + ".csv",
                names=self.MOVIE_COLUMNS, skip_first=False, separator="::")
            self._transform_csv(
                input_path=data_path + "/" + dataset_path_name + "/" + self.USERS_FILE + ".dat",
                output_path=data_path + "/" + dataset_path_name + "/" + self.USERS_FILE + ".csv",
                names=self.USER_COLUMNS, skip_first=False, separator="::")
            joint_pd = self.csv_to_joint_dataframe(data_path, dataset_path_name)
            joint_pd.to_csv(data_path + "/" + dataset_path_name + "/" + self.JOINT_FILE + ".csv", index=False)
        with tf.io.gfile.GFile(data_path + "/" + dataset_path_name + "/" + self.JOINT_FILE + ".csv") as f:
            raw_data = csv.DictReader(f)
            for row in raw_data:
                label_val = row.pop(self.RATING_COLUMN)
                yield {
                    "label": SuperDatasetBuilder.convert_to_label(str(int(float(label_val))), _LABEL_DICT),
                    "feature": {
                        name: self.RATING_FEATURE_DICT[name][1](value)
                        for name, value in row.items()
                    }
                }

    def _transform_csv(self, input_path, output_path, names, skip_first, separator=","):
      """Transform csv to a regularized format.
      Args:
        input_path: The path of the raw csv.
        output_path: The path of the cleaned csv.
        names: The csv column names.
        skip_first: Boolean of whether to skip the first line of the raw csv.
        separator: Character used to separate fields in the raw csv.
      """
      if six.PY2:
        names = [n.decode("utf-8") for n in names]
      with tf.io.gfile.GFile(output_path, "wb") as f_out, \
          tf.io.gfile.GFile(input_path, "rb") as f_in:
        # Write column names to the csv.
        f_out.write(",".join(names).encode("utf-8"))
        f_out.write(b"\n")
        for i, line in enumerate(f_in):
          if i == 0 and skip_first:
            continue  # ignore existing labels in the csv
          line = line.decode("utf-8", errors="ignore")
          fields = line.split(separator)
          if separator != ",":
            fields = ['"{}"'.format(field) if "," in field else field
                      for field in fields]
          f_out.write(",".join(fields).encode("utf-8"))

    def csv_to_joint_dataframe(self, data_dir, dataset):
        with tf.io.gfile.GFile(os.path.join(data_dir, dataset, self.RATINGS_FILE + ".csv")) as f_rating:
            ratings = pd.read_csv(f_rating, encoding="utf-8")
            with tf.io.gfile.GFile(os.path.join(data_dir, dataset, self.MOVIES_FILE + ".csv")) as f_item:
                movies = pd.read_csv(f_item, encoding="utf-8")
                df = ratings.merge(movies, on=self.ITEM_COLUMN)
                df[self.RATING_COLUMN] = df[self.RATING_COLUMN].astype(np.float32)
                df = df.drop(columns=[self.TITLE_COLUMN])
                df = self.integerize_genres(dataframe=df)
                ratings = df
            with tf.io.gfile.GFile(os.path.join(data_dir, dataset, self.USERS_FILE + ".csv")) as f_user:
                users = pd.read_csv(f_user, encoding="utf-8")
                df = ratings.merge(users, on=self.USER_COLUMN)
                df[self.RATING_COLUMN] = df[self.RATING_COLUMN].astype(np.float32)
                return df

    def integerize_genres(self, dataframe):
        """Replace genre string with a binary vector.
        Args:
          dataframe: a pandas dataframe of movie data.
        Returns:
          The transformed dataframe.
        """
        def _map_fn(entry):
            # entry.replace("Children's", "Children")  # naming difference.
            movie_genres = entry.split("|")
            output = np.zeros((len(self.GENRES),), dtype=np.int64)
            for i, genre in enumerate(self.GENRES):
                if genre in movie_genres:
                    output[i] += 1  # to one-hot vector
            return output

        def _map_fn2(entry):
            # entry.replace("Children's", "Children")  # naming difference.
            movie_genres = entry.split("|")
            num_total = 30
            output = []
            for i, genre in enumerate(self.GENRES):
                if genre in movie_genres:
                    output.append(str(i+1))   # padding 0, 有意义的下标从1开始。to [id1, id2] for embedding as: [[-0.19328298  0.1491687  -0.24025935],[0.22094809 -0.09602437 -0.01006811]]
            output = output + ['0' for i in range(len(output), num_total)]  # fill with '0' to num_total elements
            output = ",".join(output)  # e.g. convert ['12','33'] to '12,33'
            return output
        dataframe[self.GENRE_COLUMN] = dataframe[self.GENRE_COLUMN].apply(_map_fn2)
        return dataframe


if __name__ == '__main__':
    from tensorflow.python import feature_column
    embedding_featrues = {
        'price': [[1.0], [5.0], [10.0]],
        'color': [['R'], ['G'], ['B']]
    }
    price_column = feature_column.numeric_column('price')
    color_column = feature_column.categorical_column_with_vocabulary_list('color', ['R', 'G', 'B'])
    prediction = SuperDatasetBuilder.build_linear_model(embedding_featrues, [price_column, color_column]).numpy()
    print("feature_values" + "***"*40 + "\n", prediction)
    def demo_embedding():
        color_data = {"color": ["R", "B"]}
        color_column = SuperDatasetBuilder.build_categorical_column_with_vocabulary_list("color", ["R", "G", "B"])
        color_embeding = SuperDatasetBuilder.build_embedding_feature_column(color_column, 8)
        color_embeding_value = feature_column.input_layer(color_data, [color_embeding]).numpy()
        print("embedding" + "*" * 40)
        print(color_embeding_value)
    demo_embedding()

    print(SuperDatasetBuilder.list_builders())
    # build feature_columns
    feature_columns = []
    # feature_columns = MovieLensDatasetBuilder.build_numeric_feature_columns(MovieLensDatasetBuilder.camelcase_to_snakecase("MovieLensDatasetBuilder"))
    feature_columns.append(MovieLensDatasetBuilder.build_one_hot_feature_column(MovieLensDatasetBuilder.build_categorical_column_with_vocabulary_list("genres", MovieLensDatasetBuilder.GENRES)))
    # load datasets
    batched_datasets = MovieLensDatasetBuilder.load_batched_datasets(MovieLensDatasetBuilder.camelcase_to_snakecase("MovieLensDatasetBuilder"), config_name="plain_text")
    batched_dataset_features = MovieLensDatasetBuilder.read_batched_datasets(batched_datasets)
    for features, labels in batched_dataset_features:
        # print(features['genres'], tf.keras.layers.DenseFeatures(feature_columns)(features).numpy())
        print("features['genres']=", features['genres'])
    print("end!!")





