# -*- coding: utf-8 -*-
import collections
import csv
import numpy as np
import tensorflow as tf
from tensorflow.python.data.ops.dataset_ops import ConcatenateDataset

from tensorflow_datasets.core import api_utils
import tensorflow_datasets as tfds
from tensorflow.python import feature_column
from py_common_util.common.common_utils import CommonUtils
from py_common_util.tensorflow.tf_utils import TFUtils

_CITATION = """\
@ONLINE {super_dataset,
author = "Frank E. Harrell Jr., Thomas Cason",
title  = "super_dataset dataset",
month  = "oct",
year   = "2017",
url    = "https://www.openml.org/d/40945"
}
"""

_DESCRIPTION = ("Dataset describing the survival status of "
                "individual passengers on the super_dataset. Missing values in "
                "the original dataset are represented using ?. "
                "Float and int missing values are replaced with -1, string "
                "missing values are replaced with 'Unknown'.")

_EMBARKED_DICT = collections.OrderedDict([
    ("C", "Cherbourg"), ("Q", "Queenstown"), ("S", "Southampton"),
    ("?", "Unknown")
])

_PCLASS_DICT = collections.OrderedDict([
    ("1", "1st_class"), ("2", "2nd_class"), ("3", "3rd_class")
])

_SURVIVED_DICT = {"1": "survived", "0": "died"}


class DefaultDatasetBuilderConfig(tfds.core.BuilderConfig):
  """BuilderConfig for SuperDatasetBuilder."""

  @api_utils.disallow_positional_args
  def __init__(self, text_encoder_config=None, **kwargs):
    """BuilderConfig for SuperDatasetBuilder.
    Args:
      text_encoder_config: `tfds.features.text.TextEncoderConfig`, configuration
        for the `tfds.features.text.TextEncoder` used for the SuperDatasetBuilder `"text"`
        feature.
      **kwargs: keyword arguments forwarded to super.
    """
    super().__init__(**kwargs)
    self.text_encoder_config = (
        text_encoder_config or tfds.features.text.TextEncoderConfig())


class SuperDatasetBuilder(tfds.core.GeneratorBasedBuilder):
    """
    tensorflow dataset builder
    """
    BUILDER_CONFIGS = [
        DefaultDatasetBuilderConfig(
            name="plain_text",
            version="0.0.1",
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

    def __init__(self, data_dir=None, config=None):
        super().__init__(data_dir=data_dir, config=config)
        self._num_shards = 3
        self._train_data_file = "/Users/tony/tensorflow_datasets/manual_downloads/phpMYEkMl.csv"
        self._test_data_file = None
        self._validation_data_file = None

    def _info(self):
        return tfds.core.DatasetInfo(
            builder=self,
            description=_DESCRIPTION,
            features=tfds.features.FeaturesDict({
                "label": tfds.features.ClassLabel(names=["died", "survived"]),
                "feature": {name: dtype
                            for name, (dtype, func) in DEMO_FEATURE_DICT.items()},
            }),
            supervised_keys=("feature", "label"),
            urls=["https://xxx"],
            citation=_CITATION
        )

    def _split_generators(self, dl_manager):
        generator_array = []
        if self._train_data_file:
            generator_array.append(tfds.core.SplitGenerator(
                name=tfds.Split.TRAIN,
                num_shards=3,
                gen_kwargs={
                    "data_file": self._train_data_file
                }))
        if self._test_data_file:
            generator_array.append(tfds.core.SplitGenerator(
                name=tfds.Split.TEST,
                num_shards=1,
                gen_kwargs={
                    "data_file": self._test_data_file
                }))
        if self._validation_data_file:
            generator_array.append(tfds.core.SplitGenerator(
                name=tfds.Split.VALIDATION,
                num_shards=1,
                gen_kwargs={
                    "data_file": self._validation_data_file
                }))
        return generator_array

    def _generate_examples(self, **kwargs):
        """Generate features and target given the directory path.
        Args:
          file_path: path where the csv file is stored
        Yields:
          The features and the target
        """
        with tf.io.gfile.GFile(self._train_data_file) as f:
            raw_data = csv.DictReader(f)
            for row in raw_data:
                survive_val = row.pop("survived")
                yield {
                    "label": SuperDatasetBuilder.convert_to_label(survive_val, _SURVIVED_DICT),
                    "feature": {
                        name: DEMO_FEATURE_DICT[name][1](value)
                        for name, value in row.items()
                    }
                }

    @staticmethod
    def build_dataset_builder_config(name="plain_text", version="0.0.1", description="", text_encoder_config=None):
        return DefaultDatasetBuilderConfig(name=name, version=version, description=description, text_encoder_config=text_encoder_config)

    @staticmethod
    def convert_to_float(d):
      return -1.0 if d == "?" else np.float32(d)

    @staticmethod
    def convert_to_float64(d):
      return -1.0 if d == "?" else np.float64(d)

    @staticmethod
    def convert_to_int(d):
      return -1 if d == "?" else np.int32(d)  # np.int64(d) is serializable

    @staticmethod
    def convert_to_int64(d):
      return -1 if d == "?" else np.int64(d)  # np.int64(d) is serializable

    @staticmethod
    def convert_to_string(d):
      return "Unknown" if d == "?" else d

    @staticmethod
    def convert_to_label(d, dictionary):
      return dictionary[d]

    @staticmethod
    def return_same(d):
      return d

    @staticmethod
    def list_builders():
        return tfds.list_builders()

    @staticmethod
    def convert_to_int_from_string(string, dtype=np.int64, count=-1, sep=','):
        """
        @:param sep ','或'|'
        #>>> np.fromstring('8,9', dtype=np.int64,  sep=',')
        array([8, 9])
        """
        if len(string.split("|")) > 1:
            sep = "|"
        return np.fromstring(string, dtype=dtype, count=count, sep=sep)

    @staticmethod
    def convert_to_float32_from_string(string, dtype=np.float32, count=-1, sep=','):
        return SuperDatasetBuilder.convert_to_int_from_string(string, dtype, count, sep)

    @staticmethod
    def convert_to_float64_from_string(string, dtype=np.float64, count=-1, sep=','):
        return SuperDatasetBuilder.convert_to_int_from_string(string, dtype, count, sep)

    @staticmethod
    @CommonUtils.print_exec_time
    def build_and_download_and_prepare(dataset_builder_cls_name=None, config_name="plain_text"):
        dataset_builder = tfds.builder(dataset_builder_cls_name + "/" + config_name)
        dataset_builder.download_and_prepare()
        return dataset_builder.info

    @staticmethod
    @CommonUtils.print_exec_time
    def load_batched_datasets(dataset_builder_cls_name=None,
                             config_name=None,
                             split=[tfds.Split.ALL],
                             map_fn_feature_label=None,
                             batch_size:int=128,
                             shuffle:int=1000,
                             prefetch:int=10,
                             epochs:int=1) -> list:
        """
        注意：多次重新生成不同版本的数据的时候，可能需要先要手工文件夹：~/tensorflow_datasets/<<dataset_builder_cls_name>>/
        :param dataset_builder_cls_name: e.g. "mnist"
        :param config_name: e.g. "plain_text"
        :param split:
        :param map_fn_feature_label:
        e.g. def map_fn_feature_label(feature, label):
                feature = feature/255
                feature = tf.squeeze(feature)  # tf.squeeze删除大小是1的维度
                return feature, label
        :param shuffle: <1不shuffle
        :param batch_size: -1为全量数据, 或者如：SuperDatasetBuilder.get_num_examples("fashion_mnist", tfds.Split.TEST)
        :param prefetch:
        :param epochs:
        :return: list[tf.data.Dataset]:
        e.g. shape: [(num_batch, batch_size, feature_size, label_size)],
             data: [num_batch个[(feature, label),...batch_size个...,(feature, label)]]
        usage:
        batched_datasets = SuperDatasetBuilder.load_batched_datasets("recommend_dataset_builder", config_name="bytes", split=[tfds.Split.TRAIN], batch_size=128)
        for dataset in batched_datasets:
            for data in SuperDatasetBuilder.read_batched_features(dataset):
                print(data[0]["pclass"], data[1])
        # or
        for batched_examples in tfds.as_numpy(batched_datasets):
            batched_features, batched_labels = batched_examples # 对应info.supervised_keys的元素个数
        """
        dataset_name = (dataset_builder_cls_name + "/" + config_name) if config_name else dataset_builder_cls_name
        if not batch_size or batch_size < 1:
            batch_size = 1
        datasets, data_info = tfds.load(dataset_name,
                                    split=split,
                                    as_supervised=True,
                                    with_info=True,
                                    as_dataset_kwargs=dict(
                                        shuffle_files=False,
                                    ))
        batched_datasets = []  # 对应split的数据集个数
        for dataset in datasets:
            if map_fn_feature_label:
                dataset = dataset.map(map_fn_feature_label)
            if shuffle < 1:
                batched_datasets.append(dataset.batch(batch_size).prefetch(prefetch).repeat(epochs))
            else:
                batched_datasets.append(dataset.shuffle(shuffle).batch(batch_size).prefetch(prefetch).repeat(epochs))
        # if len(batched_datasets) == 1:
        #     # 1个元素的列表就直接返回该元素
        #     batched_datasets = batched_datasets[0]
        # return batched_datasets
        concated_batched_datasets = None
        for data in batched_datasets:
            if concated_batched_datasets is None:
                concated_batched_datasets = data
            else:
                concated_batched_datasets = concated_batched_datasets.concatenate(data)
        return concated_batched_datasets

    @staticmethod
    def read_batched_datasets(batched_datasets):
        """
        batched_datasets,  shape (num_batch, (batch_size个(feature, label)), e.g. (100, (128, ((28,28), (1))))
        ```
        for batched_data in MovieLensDatasetBuilder.read_batched_datasets(test_dataset):
            features, labels = batched_data
        ```
        :param batched_datasets:
        :return:
        """
        for datasets in tfds.as_numpy(batched_datasets):
            features, labels = datasets
            yield features, labels

    @staticmethod
    def split_full_datasets(full_datasets: tf.data.Dataset, num_examples=0, train_size=0.7, validation_size=0, test_size=0.3):
        """
        num_examples=total num examples | total num batched
        ```
            train_dataset, validation_dataset, test_dataset = MovieLensDatasetBuilder.split_full_datasets(full_datasets,
                                                                                                  num_examples=MovieLensDatasetBuilder.get_total_num_batch(
                                                                                                      num_examples,
                                                                                                      128),
                                                                                                  train_size=0.7,
                                                                                                  validation_size=0.1,
                                                                                                  test_size=0.2)
        ```
        """
        train_shard_num = int(train_size*10)
        train_size = int(train_size * num_examples)
        validation_shard_num = int(validation_size*10)
        validation_size = int(validation_size * num_examples)
        test_shard_num = int(test_size*10)
        test_size = int(test_size * num_examples)

        # 注意：用skip/take方法取validationh和test数据集很慢
        # train_dataset = full_datasets.take(train_size)
        # validation_dataset = full_datasets.skip(train_size).take(validation_size)
        # test_dataset = full_datasets.skip(train_size).skip(validation_size).take(test_size)

        # 注意：用skip/take方法取validationh和test数据集很慢
        # train_dataset = full_datasets.take(train_size)
        # test_dataset = full_datasets.skip(train_size)
        # validation_dataset = test_dataset.skip(validation_size)
        # test_dataset = test_dataset.take(test_size)
        # 用shard方法获取数据集比较快，注意要确保shard之后再去做shuffle的操作
        train_dataset = full_datasets.take(0)
        validation_dataset = full_datasets.take(0)
        test_dataset = full_datasets.take(0)
        for i in range(train_shard_num):
            train_dataset = train_dataset.concatenate(full_datasets.shard(10, i))
        for i in range(train_shard_num, train_shard_num + validation_shard_num):
            validation_dataset = validation_dataset.concatenate(full_datasets.shard(10, i))
        for i in range(train_shard_num + validation_shard_num, train_shard_num + validation_shard_num + test_shard_num):
            test_dataset = test_dataset.concatenate(full_datasets.shard(10, i))
        return train_dataset, validation_dataset, test_dataset

    @staticmethod
    def camelcase_to_snakecase(class_name):
        """
        Convert camel-case string to snake-case.
        usage:
        ```
        camelcase_to_snakecase(MovieLensDatasetBuilder.__name__)
        ```
        """
        return CommonUtils.camelcase_to_snakecase(class_name)

    @staticmethod
    def get_num_examples(dataset_builder_cls_name=None, split=tfds.Split.TRAIN):
        """
        获取指定数据集的长度
        :param dataset_builder_cls_name: e.g. "mnist/plain_text" 或 "mnist"
        :param split:
        :return:
        """
        return tfds.builder(dataset_builder_cls_name).info.splits[split].num_examples

    @staticmethod
    def get_total_num_batch(num_total, batch_size, allow_smaller_final_batch=True):
        return TFUtils.total_num_batch(num_total, batch_size, allow_smaller_final_batch)

    @staticmethod
    def get_info(dataset_builder_cls_name=None):
        """dataset_builder_cls_name: mnist/plain_text 或 mnist"""
        return tfds.builder(dataset_builder_cls_name).info

    @staticmethod
    def get_split_name_list(dataset_builder_cls_name=None):
        return list(tfds.builder(dataset_builder_cls_name).info.splits.keys())

    @staticmethod
    def build_all_numeric_feature_columns(dataset_builder_cls_name=None, supervised_keys_feature_name="feature"):
        """
        for tf.estimator https://www.tensorflow.org/guide/feature_columns?hl=zh-cn
        查看feature_columns的值：tf.keras.layers.DenseFeatures(feature_columns)(example).numpy()
        or tf.feature_column.input_layer(features, [feature_column]).numpy()
        构建分布式Tensorflow模型系列:特征工程 https://zhuanlan.zhihu.com/p/41663141
        :param dataset_builder_cls_name: e.g. "mnist"
        :param supervised_keys_feature_name: e.g. "image"
        :return:
        """
        feature_columns = []
        feature_types = SuperDatasetBuilder.get_info(dataset_builder_cls_name).features.dtype[supervised_keys_feature_name]
        if isinstance(feature_types, tf.dtypes.DType):
            if feature_types.is_integer or feature_types.is_floating:
                feature_columns.append(feature_column.numeric_column(supervised_keys_feature_name, dtype=feature_types))
        else:
            for feature_name in feature_types:
                feature_type = feature_types[feature_name]
                if feature_type.is_integer or feature_type.is_floating:
                    feature_columns.append(SuperDatasetBuilder.build_numeric_column(feature_name, dtype=feature_type))
        return feature_columns

    @staticmethod
    def build_numeric_feature_columns(feature_name_list, dtype=tf.float32):
        """
        for tf.estimator https://www.tensorflow.org/guide/feature_columns?hl=zh-cn
        查看feature_columns的值：tf.keras.layers.DenseFeatures(feature_columns)(example).numpy()
        or tf.feature_column.input_layer(features, [feature_column]).numpy()
        构建分布式Tensorflow模型系列:特征工程 https://zhuanlan.zhihu.com/p/41663141
        :param feature_name_list: e.g. ["user_id", "item_id]
        :param dtype:
        :return:
        """
        return [feature_column.numeric_column(feature_name, dtype=dtype) for feature_name in feature_name_list]

    @staticmethod
    def build_linear_model(features_value, combined_feature_columns=[]):
        """
        for tf.estimator https://www.tensorflow.org/guide/feature_columns?hl=zh-cn
        查看feature_columns的值：tf.keras.layers.DenseFeatures(feature_columns)(example).numpy()
        or tf.feature_column.input_layer(features, [feature_column]).numpy()
        构建分布式Tensorflow模型系列:特征工程 https://zhuanlan.zhihu.com/p/41663141
        线性模型LinearModel
        对所有特征进行线性加权操作（数值和权重值相乘）。
        ```
        from tensorflow.python import feature_column
        featrues = {
            'price': [[1.0], [5.0], [10.0]],
            'color': [['R'], ['G'], ['B']]
        }
        price_column = feature_column.numeric_column('price')
        color_column = feature_column.categorical_column_with_vocabulary_list('color', ['R', 'G', 'B'])
        prediction = SuperDatasetBuilder.build_linear_model(featrues, [price_column, color_column]).numpy()
        print("feature_values" + "***"*40 + "\n", prediction)
        结果为：
        feature_values************************************************************************************************************************
        [[0.]
        [0.]
        [0.]]
        ```
        :param features_value: dict or tf.dataset
        :param combined_feature_columns:
        :return:
        """
        return feature_column.linear_model(features_value, combined_feature_columns)

    @staticmethod
    def build_weighted_categorical_column(categorical_column, weight_feature_name):
        """
        for tf.estimator https://www.tensorflow.org/guide/feature_columns?hl=zh-cn
        查看feature_columns的值：tf.keras.layers.DenseFeatures(feature_columns)(example).numpy()
        or tf.feature_column.input_layer(features, [feature_column]).numpy()
        构建分布式Tensorflow模型系列:特征工程 https://zhuanlan.zhihu.com/p/41663141
        权重分类列WeightedCategoricalColumn
        权重改变了one-hot模式，不仅包含0或1，还带有权重值, e.g.
        [array([[1., 0., 0., 0.],
        [0., 0., 0., 5.],
        [0., 4., 0., 0.],
        [0., 0., 8., 0.],
        [3., 0., 0., 0.]], dtype=float32)]
        ```
        from tensorflow.python import feature_column
        features = {'color': [['R'], ['A'], ['G'], ['B'], ['R']],
                    'weight': [[1.0], [5.0], [4.0], [8.0], [3.0]]}
        color_f_c = feature_column.categorical_column_with_vocabulary_list(
            'color', ['R', 'G', 'B', 'A'], dtype=tf.string, default_value=-1
        )
        column = feature_column.weighted_categorical_column(color_f_c, 'weight')
        indicator = feature_column.indicator_column(column)
        feature_values = feature_column.input_layer(features, [indicator]).numpy()
        print("feature_values" + "***"*40 + "\n", feature_values)
        结果如下：
        feature_values************************************************************************************************************************
        [[1. 0. 0. 0.]
        [0. 0. 0. 5.]
        [0. 4. 0. 0.]
        [0. 0. 8. 0.]
        [3. 0. 0. 0.]]
        ```
        :param categorical_column:
        :param weight_feature_name:
        :return:
        """
        return feature_column.weighted_categorical_column(categorical_column, weight_feature_name)

    @staticmethod
    def build_one_hot_feature_column(categorical_column):
        """
        for tf.estimator https://www.tensorflow.org/guide/feature_columns?hl=zh-cn
        查看feature_columns的值：tf.keras.layers.DenseFeatures(feature_columns)(example).numpy()
        or tf.feature_column.input_layer(features, [feature_column]).numpy()
        构建分布式Tensorflow模型系列:特征工程 https://zhuanlan.zhihu.com/p/41663141
        指标列
        指标列和嵌入列从不直接处理特征，而是将分类列视为输入。
        使用指标列时，我们指示 TensorFlow 完成我们在分类 product_class 样本中看到的确切操作。
        也就是说，指标列将每个类别视为独热矢量中的一个元素，其中匹配类别的值为 1，其余类别为 0：0->[1,0,0,0]
        ```python
        name = indicator_column(categorical_column_with_vocabulary_list(
          'name', ['bob', 'george', 'wanda'])
        columns = [name, ...]
        features = tf.parse_example(..., features=make_parse_example_spec(columns))
        dense_tensor = input_layer(features, columns)
        dense_tensor == [[1, 0, 0]]  # If "name" bytes_list is ["bob"]
        dense_tensor == [[1, 0, 1]]  # If "name" bytes_list is ["bob", "wanda"]
        dense_tensor == [[2, 0, 0]]  # If "name" bytes_list is ["bob", "bob"]
        ```
        :param categorical_column:
        :return:
        """
        return feature_column.indicator_column(categorical_column)

    @staticmethod
    def build_categorical_column_with_identity(feature_name, num_buckets, default_value=None):
        """
        for tf.estimator https://www.tensorflow.org/guide/feature_columns?hl=zh-cn
        查看feature_columns的值：tf.keras.layers.DenseFeatures(feature_columns)(example).numpy()
        or tf.feature_column.input_layer(features, [feature_column]).numpy()
        构建分布式Tensorflow模型系列:特征工程 https://zhuanlan.zhihu.com/p/41663141
        ```
        分类标识列
        可将分类标识列视为分桶列的一种特殊情况。在传统的分桶列中，每个分桶表示一系列值（例如，从 1960 年到 1979 年）。
        在分类标识列中，每个分桶表示一个唯一整数。例如，假设您想要表示整数范围 [0, 4)。也就是说，您想要表示整数 0、1、2 或 3。在这种情况下，分类标识映射如下所示：
        0->[1,0,0,0]
        1->[0,1,0,0]
        2->[0,0,1,0]
        3->[0,0,0,1]
        与分桶列一样，模型可以在分类标识列中学习每个类别各自的权重。例如，我们使用唯一的整数值来表示每个类别，而不是使用某个字符串来表示 product_class。即：
        0="kitchenware"
        1="electronics"
        2="sport"
        调用 tf.feature_column.categorical_column_with_identity 以实现类别标识列。例如：
        # Create categorical output for an integer feature named "my_feature_b",
        # The values of my_feature_b must be >= 0 and < num_buckets
        identity_feature_column = tf.feature_column.categorical_column_with_identity(
            key='my_feature_b',
            num_buckets=4) # Values [0, 4)
        # In order for the preceding call to work, the input_fn() must return
        # a dictionary containing 'my_feature_b' as a key. Furthermore, the values
        # assigned to 'my_feature_b' must belong to the set [0, 4).
        def input_fn():
            ...
            return ({ 'my_feature_a':[7, 9, 5, 2], 'my_feature_b':[3, 1, 2, 2] },
                    [Label_values])
        测试代码
        import tensorflow as tf
        test = {'cat': [1,3,2,0,3]} #index分别为1,3,2,0,3
        column = tf.feature_column.categorical_column_with_identity(
            key='cat',
            num_buckets=4)
        indicator = tf.feature_column.indicator_column(column)
        tensor = tf.feature_column.input_layer(test, [indicator])
        print(tensor.numpy())
        # 输出结果
        array([[0., 1., 0., 0.],
               [0., 0., 0., 1.],
               [0., 0., 1., 0.],
               [1., 0., 0., 0.],
               [0., 0., 0., 1.]], dtype=float32)
        ```
        :param feature_name:
        :param num_buckets:
        :param default_value:
        :return:
        """
        return feature_column.categorical_column_with_identity(key=feature_name, num_buckets=num_buckets, default_value=default_value)

    @staticmethod
    def build_embedding_feature_column(categorical_column, embedding_dimension):
        """
        ref: 看Google如何实现Wide & Deep模型（2.1） https://zhuanlan.zhihu.com/p/47965313
            https://www.tensorflow.org/api_docs/python/tf/feature_column/embedding_column
        for tf.estimator https://www.tensorflow.org/guide/feature_columns?hl=zh-cn
        看Google如何实现Wide & Deep模型（2.2）https://zhuanlan.zhihu.com/p/47970601
        查看feature_columns的值：tf.keras.layers.DenseFeatures(feature_columns)(example).numpy()
        构建分布式Tensorflow模型系列:特征工程 https://zhuanlan.zhihu.com/p/41663141
        or tf.feature_column.input_layer(features, [feature_column]).numpy()
        嵌入列
        现在，假设我们有一百万个可能的类别，或者可能有十亿个，而不是只有三个。出于多种原因，随着类别数量的增加，使用指标列来训练神经网络变得不可行。
        我们可以使用嵌入列来克服这一限制。嵌入列并非将数据表示为很多维度的one-hot矢量，而是将数据表示为低维度普通矢量，其中每个单元格可以包含任意数字，
        而不仅仅是 0 或 1。通过使每个单元格能够包含更丰富的数字，嵌入列包含的单元格数量远远少于指标列。
        我们来看一个将指标列和嵌入列进行比较的示例。假设我们的输入样本包含多个不同的字词（取自仅有 81 个字词的有限词汇表）。
        我们进一步假设数据集在 4 个不同的样本中提供了下列输入字词：
        "dog"
        "spoon"
        "scissors"
        "guitar"
        处理样本时，其中一个 categorical_column_with... 函数会将样本字符串映射到分类数值。例如，一个函数将“spoon”映射到 [32]。
        （32 是我们想象出来的，实际值取决于映射函数。）然后，您可以通过下列两种方式之一表示这些分类数值：
        作为指标列。函数将每个分类数值转换为一个 81 元素的矢量（因为我们的词汇表由 81 个字词组成），
        将 1 置于分类值 (0, 32, 79, 80) 的索引处，将 0 置于所有其他位置。
        作为嵌入列。函数将分类数值 (0, 32, 79, 80) 用作对照表的索引。该对照表中的每个槽位都包含一个 3 元素矢量。
        e.g. indexs (0, 32, 79, 80) -> embedding: [[0.421,0.399,0.512],[0.312,0.632,0.412],[0.294,0.112,0.578],[0.722,0.689,0.219]]
        ```
        color_data = {"color": ["R", "B"]}
        color_column = SuperDatasetBuilder.build_categorical_column_with_vocabulary_list("color", ["R", "G", "B"])
        color_embeding = SuperDatasetBuilder.build_embedding_feature_column(color_column, 8)
        color_embeding_value = feature_column.input_layer(color_data, [color_embeding]).numpy()
        print("embedding" + "*" * 40)
        print(color_embeding_value)
        结果为：
        embedding****************************************
        [[ 0.12240461  0.41843808  0.6384718  -0.16248055  0.00317956 -0.10421363
           0.01167523 -0.11598229]
         [ 0.19527617  0.3898876   0.3911946  -0.6085922  -0.3114762   0.55712754
           0.13116577 -0.6390011 ]]
        ```
        :param categorical_column: 可以来自build_categorical_column_with_identity()
        :param embedding_dimension: 假定number_of_categories为81, 则embedding_dimension一般为：math.ceil(number_of_categories**0.25) 请注意，这只是一个一般规则；您可以根据需要设置嵌入维度的数量。
        :return:
        """
        return feature_column.embedding_column(categorical_column=categorical_column, dimension=embedding_dimension)

    @staticmethod
    def build_categorical_column_with_vocabulary_list(feature_name, vocabulary_list, default_value=0):
        """
        for tf.estimator https://www.tensorflow.org/guide/feature_columns?hl=zh-cn
        查看feature_columns的值：tf.keras.layers.DenseFeatures(feature_columns)(example).numpy()
        or tf.feature_column.input_layer(features, [feature_column]).numpy()
        构建分布式Tensorflow模型系列:特征工程 https://zhuanlan.zhihu.com/p/41663141
        categorical_column_with_vocabulary_list 根据明确的词汇表将每个字符串映射到一个整数。
        :param feature_name: e.g. age
        :param vocabulary_list: 有顺序的类别列表 e.g. ('male', 'female') or [1,2,3,4,5]
        :return:
        """
        return feature_column.categorical_column_with_vocabulary_list(feature_name, vocabulary_list, default_value=default_value)

    @staticmethod
    def build_categorical_column_with_vocabulary_file(feature_name, vocabulary_file, vocabulary_size=None, default_value=0):
        """
        for tf.estimator https://www.tensorflow.org/guide/feature_columns?hl=zh-cn
        查看feature_columns的值：tf.keras.layers.DenseFeatures(feature_columns)(example).numpy()
        or tf.feature_column.input_layer(features, [feature_column]).numpy()
        构建分布式Tensorflow模型系列:特征工程 https://zhuanlan.zhihu.com/p/41663141
        当词汇表很长时，需要输入的内容太多了。对于此类情况，
        请改为调用 tf.feature_column.categorical_column_with_vocabulary_file，
        以便将词汇放在单独的文件中。例如：
        # Given input "feature_name_from_input_fn" which is a string,
        # create a categorical feature to our model by mapping the input to one of
        # the elements in the vocabulary file
        vocabulary_feature_column =
            tf.feature_column.categorical_column_with_vocabulary_file(
                key=feature_name_from_input_fn,
                vocabulary_file="product_class.txt",
                vocabulary_size=3)
        product_class.txt 中的每个词汇元素应各占一行。在我们的示例中：
        kitchenware
        electronics
        sports
        ```
        feature_value_dict = {'letter': [["A's", 'B']]}
        categorical_feature_column = SuperDatasetBuilder.build_categorical_column_with_vocabulary_list(
            "letter", ["A's", "A", "B", "C"])
        one_hot_column = SuperDatasetBuilder.build_one_hot_column(categorical_feature_column)
        feature_values = tf.keras.layers.DenseFeatures(one_hot_column)(feature_value_dict).numpy()
        print(feature_values)
        ```
        :param feature_name: e.g. sex
        :param vocabulary_file
        :param vocabulary_size 为None是即为vocabulary_file文件的长度
        :param default_value
        :return:
        """
        return feature_column.categorical_column_with_vocabulary_file(feature_name, vocabulary_file, vocabulary_size=vocabulary_size, default_value=default_value)

    @staticmethod
    def build_categorical_column_with_hash_bucket(feature_name, hash_buckets_size=1):
        """
        for tf.estimator https://www.tensorflow.org/guide/feature_columns?hl=zh-cn
        查看feature_columns的值：tf.keras.layers.DenseFeatures(feature_columns)(example).numpy()
        or tf.feature_column.input_layer(features, [feature_column]).numpy()
        构建分布式Tensorflow模型系列:特征工程 https://zhuanlan.zhihu.com/p/41663141
        经过哈希处理的列
        到目前为止，我们处理的示例都包含很少的类别。例如，我们的 product_class 示例只有 3 个类别。
        但是通常，类别的数量非常大，以至于无法为每个词汇或整数设置单独的类别，因为这会消耗太多内存。
        对于此类情况，我们可以反问自己：“我愿意为我的输入设置多少类别？”实际上，tf.feature_column.categorical_column_with_hash_bucket 函数使您能够指定类别的数量。
        对于这种类型的特征列，模型会计算输入的哈希值，然后使用模运算符将其置于其中一个 hash_bucket_size 类别中，如以下伪代码所示：
        # pseudocode
        feature_id = hash(raw_feature) % hash_buckets_size
        创建 feature_column 的代码可能如下所示：
        hashed_feature_column =
            tf.feature_column.categorical_column_with_hash_bucket(
                key = "some_feature",
                hash_buckets_size = 100) # The number of categories
        此时，您可能会认为：“这太疯狂了！”，这种想法很正常。毕竟，我们是将不同的输入值强制划分成更少数量的类别。
        这意味着，两个可能不相关的输入会被映射到同一个类别，这样一来，神经网络也会面临同样的结果。下图显示了这一困境，
        即厨具和运动用品都被分配到类别（哈希分桶）12：
        与机器学习中的很多反直觉现象一样，事实证明哈希技术经常非常有用。这是因为哈希类别为模型提供了一些分隔方式。
        模型可以使用其他特征进一步将厨具与运动用品分隔开来。
        :param feature_name:
        :param hash_buckets_size: The number of categories e.g. 100
        :return:
        """
        hashed_feature_column = feature_column.categorical_column_with_hash_bucket(feature_name, hash_buckets_size=hash_buckets_size)
        return hashed_feature_column

    @staticmethod
    def build_bucketized_feature_column(numeric_feature_column, boundaries):
        """
        for tf.estimator https://www.tensorflow.org/guide/feature_columns?hl=zh-cn
        查看feature_columns的值：tf.keras.layers.DenseFeatures(feature_columns)(example).numpy()
        or tf.feature_column.input_layer(features, [feature_column]).numpy()
        构建分布式Tensorflow模型系列:特征工程 https://zhuanlan.zhihu.com/p/41663141
        分桶列：e.g. bucketize the numeric column on the years 1960, 1980, and 2000.
        如，将年份数据分成四个分桶，模型将按以下方式表示这些分桶：
        日期范围	表示为…
        < 1960 年	[1, 0, 0, 0]
        >= 1960 年但 < 1980 年	[0, 1, 0, 0]
        >= 1980 年但 < 2000 年	[0, 0, 1, 0]
        >= 2000 年	[0, 0, 0, 1]
        :param numeric_feature_column: e.g. tf.feature_column.numeric_column("Year")
        :param boundaries: e.g. [1960, 1980, 2000]
        :return:
        """
        bucketized_feature_column = feature_column.bucketized_column(
            source_column=numeric_feature_column,
            boundaries=boundaries)
        return bucketized_feature_column

    @staticmethod
    def build_crossed_feature_column(feature_columns=None, hash_bucket_size=10):
        """
        for tf.estimator https://www.tensorflow.org/guide/feature_columns?hl=zh-cn
        查看feature_columns的值：tf.keras.layers.DenseFeatures(feature_columns)(example).numpy()
        or tf.feature_column.input_layer(features, [feature_column]).numpy()
        构建分布式Tensorflow模型系列:特征工程 https://zhuanlan.zhihu.com/p/41663141
        组合列
        通过将多个特征组合为一个特征（称为特征组合），模型可学习每个特征组合的单独权重。
        更具体地说，假设我们希望模型计算佐治亚州亚特兰大的房产价格。这个城市的房产价格在不同位置差异很大。
        在确定对房产位置的依赖性方面，将纬度和经度表示为单独的特征用处不大；但是，将纬度和经度组合为一个特征则可精确定位位置。
        假设我们将亚特兰大表示为一个 100x100 的矩形网格区块，按纬度和经度的特征组合标识全部 10000 个区块。借助这种特征组合，
        模型可以针对与各个区块相关的房价条件进行训练，这比单独的经纬度信号强得多。
        crossed_column 仅构建 hash_bucket_size 参数所请求的数字，而不是构建这个可能非常庞大的输入表。
        特征列通过在输入元组上运行哈希函数，然后使用 hash_bucket_size 进行模运算，为索引分配一个样本。
        如前所述，执行哈希函数和模函数会限制类别的数量，但会导致类别冲突；也就是说，多个（纬度、经度）特征组合最终位于同一个哈希分桶中。
        但实际上，执行特征组合对于模型的学习能力仍具备重大价值。
        有些反直觉的是，在创建特征组合时，通常仍应在模型中包含原始（未组合）特征（如前面的代码段中所示）。
        独立的纬度和经度特征有助于模型区分组合特征中发生哈希冲突的样本。
        For example, if the input features are:
        * SparseTensor referred by first key:
        ```python
        shape = [2, 2]
        {
            [0, 0]: "a"
            [1, 0]: "b"
            [1, 1]: "c"
        }
        ```
        * SparseTensor referred by second key:
        ```python
        shape = [2, 1]
        {
            [0, 0]: "d"
            [1, 0]: "e"
        }
        ```
        then crossed feature will look like:
        ```python
        shape = [2, 2]
        {
          [0, 0]: Hash64("d", Hash64("a")) % hash_bucket_size
          [1, 0]: Hash64("e", Hash64("b")) % hash_bucket_size
          [1, 1]: Hash64("e", Hash64("c")) % hash_bucket_size
        }
        ```
        :param feature_columns:
        :param hash_bucket_size:
        :return:
        """
        return feature_column.crossed_column(feature_columns, hash_bucket_size)


DEMO_FEATURE_DICT = collections.OrderedDict([
    ("pclass", (tfds.features.ClassLabel(names=_PCLASS_DICT.values()),
                lambda d: SuperDatasetBuilder.convert_to_label(d, _PCLASS_DICT))),
    ("name", (tf.string, SuperDatasetBuilder.convert_to_string)),
    ("sex", (tfds.features.ClassLabel(names=["male", "female"]), SuperDatasetBuilder.return_same)),
    ("age", (tf.float32, SuperDatasetBuilder.convert_to_float)),
    ("sibsp", (tf.int32, SuperDatasetBuilder.convert_to_int)),
    ("parch", (tf.int32, SuperDatasetBuilder.convert_to_int)),
    ("ticket", (tf.string, SuperDatasetBuilder.convert_to_string)),
    ("fare", (tf.float32, SuperDatasetBuilder.convert_to_float)),
    ("cabin", (tf.string, SuperDatasetBuilder.convert_to_string)),
    ("embarked", (tfds.features.ClassLabel(names=_EMBARKED_DICT.values()),
                  lambda d: SuperDatasetBuilder.convert_to_label(d, _EMBARKED_DICT))),
    ("boat", (tf.string, SuperDatasetBuilder.convert_to_string)),
    ("body", (tf.int32, SuperDatasetBuilder.convert_to_int)),
    ("home.dest", (tf.string, SuperDatasetBuilder.convert_to_string))
])