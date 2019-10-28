# -*- coding: utf-8 -*-
import tensorflow as tf
import tensorflow_datasets as tfds
import six
import csv
import collections
import pandas as pd
from skydl.datasets.super_tf_dataset_builder import DefaultDatasetBuilderConfig, SuperDatasetBuilder
import os,sys
sys.path.append(os.path.abspath('%s/..' % sys.path[0]))


class RecommendDatasetBuilder(SuperDatasetBuilder):
    """
    资讯智能推荐系统中用于精排序模型的数据集
    """
    BUILDER_CONFIGS = [
        DefaultDatasetBuilderConfig(
            name="plain_text",
            version="0.0.3",
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

    # 数据的列名
    MEMBER_ID_COLUMN = "member_id"   # 用户id（不需要出现在训练集里）
    CONTENT_ID_COLUMN = "content_id" # 内容ID（不需要出现在训练集里）
    GENDER_COLUMN = "gender"  # 性别
    AGE_GROUP_COLUMN = "age_group" # 年龄段
    POSITION_COLUMN = "position" # 职业
    ANNUAL_INCOME_COLUMN = "annual_income" # 年收入
    ADDRESS_COLUMN = "address" # 地区
    ACCOUNT_TYPE_COLUMN = "account_type" # 账户类型
    ASSET_SIZE_COLUMN = "asset_size" # 资产规模
    INVESTMENT_RISK_PREFERENCE_COLUMN = "Investment_risk_preference" # 投资风险偏好
    MARKET_PREFERENCE_COLUMN = "Market_preference" # 市场偏好
    CONTENT_TYPE_COLUMN = "content_type" # 资讯内容类型
    TAG_INDEX_COLUMN = "tag_indexs" # 标签索引列表字符串, 用|分割开，只截取20个，不足20个后面补0
    TAG_INDEX_COUNT_COLUMN = "tag_index_count"  # 标签索引的总数量
    TARGET_COLUMN = "target"  # 训练目标，目前只有值1，后面引入阅读时长，阅读次数，不感兴趣这些因素

    LABEL_DICT = collections.OrderedDict([
        ("1", "1st_class")
    ])

    FEATURE_DICT = collections.OrderedDict([
        ("member_id", (tf.int32, SuperDatasetBuilder.convert_to_int)),
        ("content_id", (tf.int64, SuperDatasetBuilder.convert_to_int64)),
        ("gender", (tf.float32, SuperDatasetBuilder.convert_to_float)),
        ("age_group", (tf.float32, SuperDatasetBuilder.convert_to_int)),
        ("position", (tf.float32, SuperDatasetBuilder.convert_to_int)),
        ("annual_income", (tf.float32, SuperDatasetBuilder.convert_to_int)),
        ("address", (tf.float32, SuperDatasetBuilder.convert_to_int)),
        ("account_type", (tf.float32, SuperDatasetBuilder.convert_to_int)),
        ("asset_size", (tf.float32, SuperDatasetBuilder.convert_to_int)),
        ("Investment_risk_preference", (tf.float32, SuperDatasetBuilder.convert_to_int)),
        ("Market_preference", (tf.float32, SuperDatasetBuilder.convert_to_int)),
        ("content_type", (tf.float32, SuperDatasetBuilder.convert_to_int)),
        ("tag_indexs", (tfds.features.Tensor(dtype=tf.float32, shape=(None,)), SuperDatasetBuilder.convert_to_float32_from_string)),
        ("tag_index_count", (tf.int64, SuperDatasetBuilder.convert_to_int64))
        # 在_generate_examples()里单独处理了target列，这里不需要重复定义
    ])

    def __init__(self, data_dir=None, config=None):
        super().__init__(data_dir=data_dir, config=config)
        self._num_shards = 1
        self._train_data_file = os.getenv("HOME") + "/tmp/news_recommend_system_job/ranking_train_dataset.csv"
        self._test_data_file = None
        self._validation_data_file = None

    def _info(self):
        return tfds.core.DatasetInfo(
            builder=self,
            description=("recommend sorting dataset"),
            features=tfds.features.FeaturesDict({
                "label": tfds.features.ClassLabel(names=[label for label in self.LABEL_DICT.values()]),
                "feature": {name: dtype
                            for name, (dtype, func) in self.FEATURE_DICT.items()},
            }),
            supervised_keys=("feature", "label"),
            urls=["https://xxx"],
            citation="@ONLINE {recommend sorting dataset}"
        )

    def _split_generators(self, dl_manager):
        generator_array = []
        if self._train_data_file:
            generator_array.append(tfds.core.SplitGenerator(
                name=tfds.Split.TRAIN,
                num_shards=3,
                gen_kwargs={
                    "data_path": self._train_data_file
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
        with tf.io.gfile.GFile(data_path) as f:
            raw_data = csv.DictReader(f)
            for row in raw_data:
                label_val = row.pop(self.TARGET_COLUMN)
                yield {
                    "label": SuperDatasetBuilder.convert_to_label(str(int(float(label_val))), self.LABEL_DICT),
                    "feature": {
                        name: self.FEATURE_DICT[name][1](value)
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
        with tf.io.gfile.GFile(os.path.join(data_dir)) as f_data:
            return pd.read_csv(f_data, encoding="utf-8")


if __name__ == '__main__':
    # load datasets
    dataset_name = RecommendDatasetBuilder.camelcase_to_snakecase("RecommendDatasetBuilder")
    print(SuperDatasetBuilder.list_builders())
    batched_datasets = RecommendDatasetBuilder.load_batched_datasets(dataset_name, config_name="plain_text")
    batched_dataset_features = RecommendDatasetBuilder.read_batched_datasets(batched_datasets)
    for features, labels in batched_dataset_features:
        print("tag_index_count=" + str(features['tag_index_count']) + ", features['tag_indexs']=", features['tag_indexs'])
    print("end!!")




