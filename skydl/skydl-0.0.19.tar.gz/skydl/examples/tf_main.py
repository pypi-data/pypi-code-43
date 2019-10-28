# -*- coding: utf-8 -*-
import tensorflow as tf
import tensorflow_datasets as tfds
import numpy as np
import sys, os
from skydl.datasets.movielens_dataset_builder import MovieLensDatasetBuilder
from skydl.model.default_model import DefaultModel
from tensorflow import keras
from py_common_util.common.common_utils import CommonUtils
from skydl.model.impl.movielens_wide_deep_keras_model import MovieLensWideDeepKerasModel
from skydl.model.impl.movielens_wide_deep_keras_model1 import MovieLensWideDeepKerasModel1
from skydl.model.impl.movielens_wide_deep_keras_model2 import MovieLensWideDeepKerasModel2
from skydl.model.keras_feature_input_layer_merged_model import KerasFeatureInputMergedModel
sys.path.append(os.path.abspath('%s/..' % sys.path[0]))


@CommonUtils.print_exec_time
def run_default_model():
    DefaultModel().fit()


@CommonUtils.print_exec_time
def run_keras_model():
    from skydl.model.impl.my_keras_model import MyKerasModel
    # feature_columns = [tf.feature_column.numeric_column("image", shape=[28, 28])]
    MyKerasModel("my_keras_model", [
        keras.layers.Flatten(input_shape=(28, 28)),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dense(10, activation='softmax', name="prediction")
    ]).compile(
        keras.losses.sparse_categorical_crossentropy,
        keras.optimizers.Adam(),
        ['accuracy']
        # ['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    ).fit().serving()

    inference_model = MyKerasModel()
    _, evaluate_dataset, _ = inference_model.load_data()
    import tensorflow_datasets as tfds
    for dataset in tfds.as_numpy(evaluate_dataset):
        features, labels = dataset
    print("inference model name: ", inference_model.model.name())
    # inference_model.inference(model_name="my_keras_model",
    #                           features_list=features.tolist()[:2])
    # print("the inference results:", labels.tolist()[:2])


@CommonUtils.print_exec_time
def run_wine_wide_deep_keras_model():
    from skydl.model.impl.wine_wide_deep_keras_model import WineWideDeepKerasModel
    WineWideDeepKerasModel("wine_wide_deep_keras_model", [
        keras.layers.Flatten(input_shape=(28, 28)),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dense(10, activation='softmax', name="prediction")
    ]).compile(
        keras.losses.sparse_categorical_crossentropy,
        keras.optimizers.Adam(),
        ['accuracy']
    ).fit()


@CommonUtils.print_exec_time
def run_movielens_wide_deep_keras_model_ok():
    from skydl.model.impl.movielens_wide_deep_keras_model import MovieLensWideDeepKerasModel
    MovieLensWideDeepKerasModel("movielens_wide_deep_keras_model1", [
        keras.layers.Dense(units=128, activation='relu'),
        keras.layers.Flatten()
    ]).compile(
        loss="mean_squared_error",
        optimizer="adam",
        metrics=['accuracy']
    ).fit_ok()


@CommonUtils.print_exec_time
def run_movielens_wide_deep_keras_model():
    """
    1.Best Practices on Recommendation Systems https://github.com/microsoft/recommenders
    1.图书推荐，参考：Book Recommendation System https://github.com/TannerGilbert/Tutorials/blob/master/Recommendation%20System/Recommendation%20System.ipynb
    2.Building a book Recommendation System using Keras https://towardsdatascience.com/building-a-book-recommendation-system-using-keras-1fba34180699
    3.How to Implement a Recommendation System with Deep Learning and PyTorch https://medium.com/@iliazaitsev/how-to-implement-a-recommendation-system-with-deep-learning-and-pytorch-2d40476590f9
    """
    from skydl.model.impl.movielens_wide_deep_keras_model import MovieLensWideDeepKerasModel
    from skydl.datasets.movielens_dataset_builder import MovieLensDatasetBuilder
    dataset_name = MovieLensDatasetBuilder.camelcase_to_snakecase("MovieLensDatasetBuilder")
    num_examples = MovieLensDatasetBuilder.get_num_examples(dataset_name)
    full_datasets = MovieLensDatasetBuilder.load_batched_datasets(dataset_name,
                                                                  split=[tfds.Split.TRAIN],
                                                                  batch_size=128,
                                                                  epochs=1)
    train_dataset, validation_dataset, test_dataset = MovieLensDatasetBuilder.split_full_datasets(full_datasets,
                                                                                                  num_examples=MovieLensDatasetBuilder.get_total_num_batch(
                                                                                                      num_examples,
                                                                                                      128),
                                                                                                  train_size=0.7,
                                                                                                  validation_size=0,
                                                                                                  test_size=0.2)
    np_user_ids = np.array([])
    np_item_ids = np.array([])
    np_labels = np.array([])

    # train_dataset = full_datasets.take(100) # for dev
    for features, labels in MovieLensDatasetBuilder.read_batched_datasets(train_dataset.take(100)):
        np_user_ids = np.append(np_user_ids, features['user_id'])
        np_item_ids = np.append(np_item_ids, features['item_id'])
        np_labels = np.append(np_labels, labels)

    user_feature_column = MovieLensDatasetBuilder.build_numeric_feature_columns(["user_id"])
    item_feature_column = MovieLensDatasetBuilder.build_numeric_feature_columns(["item_id"])
    total_users = len(np.unique(np_user_ids))
    total_items = len(np.unique(np_item_ids))

    user_model = MovieLensWideDeepKerasModel("user_movielens_wide_deep_keras_model", [
        keras.layers.Input(shape=(1,), name="age"),
        keras.layers.Embedding(total_users, 10),
        keras.layers.Dense(units=128, activation='relu'),
        keras.layers.Flatten()
    ]).compile(
        loss="mean_squared_error",
        optimizer="adam",
        metrics=['accuracy']
    )

    item_model = MovieLensWideDeepKerasModel("item_movielens_wide_deep_keras_model", [
        keras.layers.Input(shape=(1,), name="timestamp"),
        keras.layers.Embedding(total_items, 10),
        keras.layers.Dense(units=128, activation='relu'),
        keras.layers.Flatten()
    ]).compile(
        loss="mean_squared_error",
        optimizer="adam",
        metrics=['accuracy']
    )

    # merged model
    keras_feature_column_input_layer, keras_pure_input_layer_dict = \
        KerasFeatureInputMergedModel.build_keras_feature_column_output_layer(train_dataset.take(1),
                                                                            user_feature_column+item_feature_column,
                                                                            ["user_id", "item_id"])
    merged_outputs = keras.layers.concatenate([user_model.model.get_static_logits_output(), item_model.model.get_static_logits_output(), keras_feature_column_input_layer])
    merged_outputs = keras.layers.Dense(1)(merged_outputs)
    merged_inputs = [user_model.model.get_static_first_input(), item_model.model.get_static_first_input()] + list(keras_pure_input_layer_dict.values())

    merged_model = MovieLensWideDeepKerasModel(
        "merged_movielens_wide_deep_keras_model",
        keras_inputs=merged_inputs,
        keras_outputs=merged_outputs
    ).compile(
        loss="binary_crossentropy",
        optimizer="adam",
        metrics=['accuracy']
    )
    merged_model.model.model_proxy.fit(train_dataset)
    merged_model.model.model_proxy.summary()


@CommonUtils.print_exec_time
def run_my_estimator_model():
    from tensorflow_estimator import estimator
    from tensorflow.python import feature_column
    from skydl.model.impl.my_estimator_model import MyEstimatorModel
    from tfv2 import iris_data
    batch_size = 128
    train_steps = 10

    # Fetch the data
    (train_x, train_y), (test_x, test_y) = iris_data.load_data()

    # Feature columns describe how to use the input.
    my_feature_columns = []
    for key in train_x.keys():
        my_feature_columns.append(feature_column.numeric_column(key=key))
    def my_model(features, labels, mode, params):
        """DNN with three hidden layers and learning_rate=0.1."""
        # Create three fully connected layers.
        net = feature_column.input_layer(features, params['feature_columns'])
        for units in params['hidden_units']:
            net = tf.compat.v1.layers.dense(net, units=units, activation=tf.nn.relu)
        # Compute logits (1 per class).
        logits = tf.compat.v1.layers.dense(net, params['n_classes'], activation=None)
        # Compute predictions.
        predicted_classes = tf.argmax(logits, 1)
        if mode == estimator.ModeKeys.PREDICT:
            predictions = {
                'class_ids': predicted_classes[:, tf.newaxis],
                'probabilities': tf.nn.softmax(logits),
                'logits': logits,
            }
            return estimator.EstimatorSpec(mode, predictions=predictions)
        # Compute loss.
        loss = tf.compat.v1.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)
        # Compute evaluation metrics.
        accuracy = tf.compat.v1.metrics.accuracy(labels=labels,
                                                 predictions=predicted_classes,
                                                 name='acc_op')
        metrics = {'accuracy': accuracy}
        tf.summary.scalar('accuracy', accuracy[1])
        if mode == estimator.ModeKeys.EVAL:
            return estimator.EstimatorSpec(mode, loss=loss, eval_metric_ops=metrics)
        # Create training op.
        assert mode == estimator.ModeKeys.TRAIN
        optimizer = tf.compat.v1.train.AdagradOptimizer(learning_rate=0.1)
        train_op = optimizer.minimize(loss, global_step=tf.compat.v1.train.get_global_step())
        return estimator.EstimatorSpec(mode, loss=loss, train_op=train_op)

    MyEstimatorModel("my_estimator_model",
                     model_fn=my_model,
                     params={
                        'feature_columns': my_feature_columns,
                        'hidden_units': [10, 10],
                        'n_classes': 3
                    }).compile().fit()


@CommonUtils.print_exec_time
def run_my_estimator_model2():
    import pandas as pd
    from tensorflow_estimator import estimator
    from tensorflow.python import feature_column
    from skydl.model.impl.my_estimator_model import MyEstimatorModel
    from skydl.datasets.super_tf_dataset_builder import SuperDatasetBuilder
    batch_size = 128
    train_steps = 10
    dftrain = pd.read_csv('https://storage.googleapis.com/tf-datasets/titanic/train.csv')
    dfeval = pd.read_csv('https://storage.googleapis.com/tf-datasets/titanic/eval.csv')

    y_train = dftrain.pop('survived')
    y_eval = dfeval.pop('survived')
    tf.random.set_seed(123)
    fc = feature_column
    CATEGORICAL_COLUMNS = ['sex', 'n_siblings_spouses', 'parch', 'class', 'deck', 'embark_town', 'alone']
    NUMERIC_COLUMNS = ['age', 'fare']

    feature_columns = []
    for feature_name in CATEGORICAL_COLUMNS:
        # Need to one-hot encode categorical features.
        vocabulary = dftrain[feature_name].unique()
        feature_columns.append(SuperDatasetBuilder.build_one_hot_column(SuperDatasetBuilder.build_categorical_column_with_vocabulary_list(feature_name, vocabulary)))

    for feature_name in NUMERIC_COLUMNS:
        feature_columns.append(SuperDatasetBuilder.build_numeric_column(feature_name, dtype=tf.float32))

    example = dict(dftrain.head(1))
    class_fc = SuperDatasetBuilder.build_one_hot_column(SuperDatasetBuilder.build_categorical_column_with_vocabulary_list('class', ('First', 'Second', 'Third')))
    print('Feature value: "{}"'.format(example['class'].iloc[0]))
    print('One-hot encoded: ', tf.keras.layers.DenseFeatures([class_fc])(example).numpy())

    est = estimator.BoostedTreesClassifier(feature_columns, n_batches_per_layer=batch_size)
    MyEstimatorModel("my_estimator_model2",
                     model_fn=est.model_fn).compile().fit2()


@CommonUtils.print_exec_time
def run_keras_model_to_estimator():
    from skydl.model.impl.my_keras_model import MyKerasModel
    model = MyKerasModel("my_keras_model_to_estimator", [
        keras.layers.Flatten(input_shape=(28, 28)),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dense(10, activation='softmax', name="prediction")
    ]).compile(
        keras.losses.sparse_categorical_crossentropy,
        keras.optimizers.Adam(),
        ['accuracy']
        # ['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )
    estimator = model.model_to_estimator()
    estimator.train(input_fn=lambda: model.load_data()[0])
    print("eval...........")
    result = estimator.evaluate(input_fn=lambda: model.load_data()[1])
    import pandas as pd
    print(pd.Series(result))


@CommonUtils.print_exec_time
def run_hst_recommend_system():
    """推荐系统：协同过滤"""
    from skydl.model.impl.movielens_wide_deep_keras_model import MovieLensWideDeepKerasModel
    train_dataset, validation_dataset, evaluate_dataset, np_user_ids, np_item_ids, np_labels = MovieLensWideDeepKerasModel().load_data()
    total_users = max(np.unique(np_user_ids))
    total_items = max(np.unique(np_item_ids))
    print("***total_users，total_items=***", total_users, total_items)  # 6040 3649

    user_model = MovieLensWideDeepKerasModel1("user_recommend", [
        keras.layers.Input(shape=(1,), name="user_id"),
        keras.layers.Embedding(6040, 10),
        keras.layers.Flatten()
    ])

    item_model = MovieLensWideDeepKerasModel2("item_recommend", [
        keras.layers.Input(shape=(1,), name="item_id"),
        keras.layers.Embedding(4000, 10),
        keras.layers.Flatten()
    ])

    # merged model
    merged_outputs = keras.layers.Dot(axes=1)([item_model.model.get_static_logits_output(), user_model.model.get_static_logits_output()])
    merged_outputs = keras.layers.Dense(1)(merged_outputs)
    merged_inputs = [user_model.model.get_static_first_input(), item_model.model.get_static_first_input()]

    print("inference instances: ", [{"user_id": np_user_ids[3], "item_id": np_item_ids[i]} for i in range(len(np_item_ids[:400]))])
    MovieLensWideDeepKerasModel(
        "user_book_recommend",
        keras_inputs=merged_inputs,
        keras_outputs=merged_outputs
    ).compile(
        loss="mean_squared_error",
        optimizer="adam",
        metrics=['accuracy']
    ).fit(
        loaded_dataset=[train_dataset, validation_dataset, evaluate_dataset, np_user_ids, np_item_ids, np_labels]
    ).serving(
    ).inference(tfx_host_port="http://192.168.83.111:8501/",
                model_name="user_book_recommend",
                features_list=[{"user_id": np_user_ids[3], "item_id": np_item_ids[i]} for i in range(len(np_item_ids[:400]))])


@CommonUtils.print_exec_time
def run_hst_recommend_system1():
    """推荐系统：协同过滤"""
    from skydl.model.impl.movielens_wide_deep_keras_model import MovieLensWideDeepKerasModel
    train_dataset, validation_dataset, evaluate_dataset, np_user_ids, np_item_ids, np_labels = MovieLensWideDeepKerasModel().load_data()
    total_users = max(np.unique(np_user_ids))
    total_items = max(np.unique(np_item_ids))
    print("***total_users，total_items=***", total_users, total_items)  # 6040 3649

    keras_feature_column_output_layer1, keras_pure_input_layer_dict1 = \
        KerasFeatureInputMergedModel.build_keras_feature_column_output_layer(train_dataset.take(1),
                                                                            MovieLensDatasetBuilder.build_numeric_feature_columns(["user_id"], dtype=tf.int32),
                                                                            ["user_id"])

    keras_feature_column_output_layer2, keras_pure_input_layer_dict2 = \
        KerasFeatureInputMergedModel.build_keras_feature_column_output_layer(train_dataset.take(1),
                                                                            MovieLensDatasetBuilder.build_numeric_feature_columns(["item_id"], dtype=tf.int32),
                                                                            ["item_id"])

    # keras_feature_column_output_layer3, keras_pure_input_layer_dict3 = \
    #     KerasFeatureInputMergedModel.build_keras_feature_column_output_layer(train_dataset.take(1),
    #                                                                         MovieLensDatasetBuilder.build_numeric_feature_columns(["genres"], dtype=tf.int64),
    #                                                                         ["genres"])
    keras_feature_column_output_layer3, keras_pure_input_layer_dict3 = \
        KerasFeatureInputMergedModel.build_keras_feature_column_output_layer(train_dataset.take(1),
                                                                            MovieLensDatasetBuilder.build_embedding_feature_column(MovieLensDatasetBuilder.build_categorical_column_with_identity("genres", num_buckets=30), 10),
                                                                            ["genres"])

    out1 = keras.layers.Flatten()(keras.layers.Embedding(6040, 10)(keras_feature_column_output_layer1))
    out2 = keras.layers.Flatten()(keras.layers.Embedding(4000, 10)(keras_feature_column_output_layer2))
    # out3 = keras.layers.Flatten()(keras.layers.Embedding(29+1, 10, mask_zero=False)(keras_feature_column_output_layer3))
    out3 = keras_feature_column_output_layer3

    # merged model
    merged_outputs = keras.layers.Dot(axes=1)([out1, out3])
    merged_outputs = keras.layers.Dense(1)(merged_outputs)
    merged_inputs = [keras_pure_input_layer_dict1, keras_pure_input_layer_dict3]

    print("inference instances: ", [{"user_id": np_user_ids[3], "item_id": np_item_ids[i]} for i in range(len(np_item_ids[:400]))])
    MovieLensWideDeepKerasModel(
        "user_book_recommend",
        keras_inputs=merged_inputs,
        keras_outputs=merged_outputs
    ).compile(
        loss="mean_squared_error",
        optimizer="adam",
        metrics=['accuracy']
    ).fit(
        loaded_dataset=[train_dataset, validation_dataset, evaluate_dataset, np_user_ids, np_item_ids, np_labels]
    ).serving(
    ).inference(tfx_host_port="http://192.168.83.111:8501/",
                model_name="user_book_recommend",
                features_list=[{"user_id": np.array([4768]).tolist(), "genres": np.array([12,28,5,7,20,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], np.int64).tolist()} for i in range(len(np_item_ids[:400]))])
    # ).inference(tfx_host_port="http://192.168.83.111:8501/",
    #             model_name="user_book_recommend",
    #             features_list=[{"user_id": np_user_ids[3].tolist(), "item_id": np_item_ids[i].tolist()} for i in range(len(np_item_ids[:400]))])


@CommonUtils.print_exec_time
def run_hst_recommend_system2():
    """推荐系统：协同过滤"""
    from skydl.model.impl.movielens_wide_deep_keras_model import MovieLensWideDeepKerasModel
    train_dataset, validation_dataset, test_dataset, np_user_ids, np_item_ids, np_labels = MovieLensWideDeepKerasModel().load_data()
    total_users = len(np.unique(np_user_ids))
    total_items = len(np.unique(np_item_ids))
    print("******", total_users, total_items)  # 6040 3650

    # first model
    first_input = keras.layers.Input(shape=(1,), name='user_id')
    first_input_encoded = keras.layers.Embedding(input_dim=6040, output_dim=3, input_length=1)(first_input)
    first_input_encoded = keras.layers.Reshape((3,))(first_input_encoded)

    # second model
    second_input = keras.layers.Input(shape=(1,), name='item_id')
    second_input_encoded = keras.layers.Embedding(input_dim=4000, output_dim=3, input_length=1)(second_input)
    second_input_encoded = keras.layers.Reshape((3,))(second_input_encoded)

    # merged model
    merged_outputs = keras.layers.Dot(axes=1)([first_input_encoded, second_input_encoded])
    merged_outputs = keras.layers.Dense(1)(merged_outputs)

    print("inference instances: ", [{"user_id": np_user_ids[3], "item_id": np_item_ids[i]} for i in range(len(np_item_ids[:400]))])
    MovieLensWideDeepKerasModel(
        "user_book_recommend",
        keras_inputs=[first_input, second_input],
        keras_outputs=merged_outputs
    ).compile(
        loss="mean_squared_error",
        optimizer="adam",
        metrics=['accuracy']
    ).fit(
        loaded_dataset=[train_dataset, validation_dataset, test_dataset, np_user_ids, np_item_ids, np_labels]
    ).serving(
    ).inference(tfx_host_port="http://192.168.83.111:8501/",
                model_name="user_book_recommend",
                features_list=[{"user_id": np_user_ids[3], "item_id": np_item_ids[i]} for i in range(len(np_item_ids[:400]))])


@CommonUtils.print_exec_time
def keras_input_will_ok_no_need_delete():
    import pandas as pd
    df = pd.DataFrame(
        [[3, 4, 8, 0],
         [2, 6, 9, 1]],
        columns=['user_id', 'item_id', 'other_id', 'target'])

    def df_to_dataset(dataframe, shuffle=True, batch_size=32):
        dataframe = dataframe.copy()
        labels = dataframe.pop('target')
        d = dict(dataframe)
        ds = tf.data.Dataset.from_tensor_slices((d, labels))
        if shuffle:
            ds = ds.shuffle(buffer_size=len(dataframe))
        ds = ds.batch(batch_size)
        return ds
    train_ds = df_to_dataset(df)
    val_ds = df_to_dataset(df)

    # first model
    first_input = keras.layers.Input(shape=(1,), name='user_id')
    first_input_encoded = keras.layers.Embedding(input_dim=10, output_dim=3, input_length=1)(first_input)
    first_input_encoded = keras.layers.Reshape((3,))(first_input_encoded)

    # second model
    second_input = keras.layers.Input(shape=(1,), name='item_id')
    second_input_encoded = keras.layers.Embedding(input_dim=10, output_dim=3, input_length=1)(second_input)
    second_input_encoded = keras.layers.Reshape((3,))(second_input_encoded)

    merged_outputs = keras.layers.concatenate([first_input_encoded, second_input_encoded])
    merged_outputs = keras.layers.Dense(1)(merged_outputs)
    MovieLensWideDeepKerasModel(
        "user_book_xxx",
        keras_inputs=[first_input, second_input],
        keras_outputs=merged_outputs
    ).compile(
        loss="mean_squared_error",
        optimizer="adam",
        metrics=['accuracy']
    ).fit_xxx(
        loaded_dataset=[train_ds, val_ds]
    ).predict_xxx()


def nlp_ragged_tensor():
    # TensorFlow 2.0新特性之Ragged Tensor  http://www.sohu.com/a/306300588_723464
    import math
    num_buckets = 1024
    embedding_size = 16
    embedding_table = tf.Variable(tf.random.truncated_normal([num_buckets, embedding_size], stddev=1.0 / math.sqrt(embedding_size)), name="embedding_table")
    queries = tf.ragged.constant([['Who', 'is', 'Dan', 'Smith'],
                                  ['Pause'],
                                  ['Will', 'it', 'rain', 'later', 'today']
                                  ])
    word_buckets = tf.strings.to_hash_bucket_fast(queries, num_buckets)
    word_embeddings = tf.ragged.map_flat_values(tf.nn.embedding_lookup, embedding_table, word_buckets)
    marker = tf.fill([queries.nrows(), 1], '#')
    padded = tf.concat([marker, queries, marker], axis=1)  # ②
    # Build word bigrams & look up embeddings.
    bigrams = tf.strings.join([padded[:, :-1], padded[:, 1:]], separator='+')  # ③
    bigram_buckets = tf.strings.to_hash_bucket_fast(bigrams, num_buckets)
    bigram_embeddings = tf.ragged.map_flat_values(tf.nn.embedding_lookup, embedding_table, bigram_buckets)  # ④
    # Find the average embedding for each sentence
    all_embeddings = tf.concat([word_embeddings, bigram_embeddings], axis=1)  # ⑤
    avg_embedding = tf.reduce_mean(all_embeddings, axis=1)  # ⑥
    print(word_embeddings)
    print(bigram_embeddings)
    print(all_embeddings)
    print(avg_embedding)


def run_ray():
    import ray, time

    def print_something():
        print("123")

    @ray.remote
    def f():
        time.sleep(1)
        print_something()
        return 1

    ray.init()
    results = ray.get([f.remote() for i in range(4)])
    print(results)

def will_fail_not_need_delete():
    # from keras_feature_input_layer_merged_model.py
    import pandas as pd
    from tensorflow import feature_column
    from tensorflow import keras

    feature_columns = []
    child_gender_young = feature_column.categorical_column_with_vocabulary_list(
        'child_gender_young', ['boy', 'girl', ''])
    child_gender_young_one_hot = feature_column.indicator_column(child_gender_young)
    feature_columns.append(child_gender_young_one_hot)

    child_month_young = feature_column.numeric_column("child_month_young")
    kid_age_youngest_buckets = feature_column.bucketized_column(child_month_young, boundaries=[0, 12, 24, 36, 72, 96])
    feature_columns.append(kid_age_youngest_buckets)

    def keras_merged_model_fn(train_dataset, feature_columns, feature_column_names=["child_month_young", "child_gender_young"]):
        # first model
        first_input = keras.layers.Input(shape=(1,), name='first_input')
        first_input_encoded = keras.layers.Embedding(input_dim=10, output_dim=3, input_length=1)(first_input)
        first_input_encoded = keras.layers.Reshape((3,))(first_input_encoded)

        # second model
        second_input = keras.layers.Input(shape=(1,), name='second_input')
        second_input_encoded = keras.layers.Embedding(input_dim=10, output_dim=3, input_length=1)(second_input)
        second_input_encoded = keras.layers.Reshape((3,))(second_input_encoded)

        # merged model
        keras_feature_column_output_layer, keras_pure_input_layer_dict = \
            KerasFeatureInputMergedModel.build_keras_feature_column_output_layer(train_dataset.take(1),
                                                                            feature_columns,
                                                                            feature_column_names)
        merged_outputs = keras.layers.concatenate([first_input_encoded, second_input_encoded, keras_feature_column_output_layer])
        merged_outputs = keras.layers.Dense(1)(merged_outputs)

        merged_inputs = [first_input, second_input] + list(keras_pure_input_layer_dict.values())
        merged_model = keras.Model(inputs=merged_inputs, outputs=merged_outputs)
        return merged_model

    df = pd.DataFrame(
        [[3, 4, 5, 'boy', 0],
         [2, 6, 7, 'girl', 1]],
        columns=['first_input', 'second_input', 'child_month_young', 'child_gender_young', 'target'])

    def df_to_dataset(dataframe, shuffle=True, batch_size=32):
        dataframe = dataframe.copy()
        labels = dataframe.pop('target')
        d = dict(dataframe)
        ds = tf.data.Dataset.from_tensor_slices((d, labels))
        if shuffle:
            ds = ds.shuffle(buffer_size=len(dataframe))
        ds = ds.batch(batch_size)
        return ds

    train_ds = df_to_dataset(df)
    val_ds = df_to_dataset(df)

    merged_model = keras_merged_model_fn(train_ds, feature_columns, feature_column_names=["child_month_young", "child_gender_young"])
    merged_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    merged_model.fit(train_ds, validation_data=val_ds, epochs=1)


def result_is_ok_can_not_delete():
    # from: https://github.com/tensorflow/tensorflow/issues/27416
    import pandas as pd
    # !pip install tensorflow==2.0.0-alpha0
    import tensorflow as tf
    from tensorflow import feature_column
    from tensorflow import keras
    from tensorflow.keras import layers
    from sklearn.model_selection import train_test_split

    URL = 'https://storage.googleapis.com/applied-dl/heart.csv'
    dataframe = pd.read_csv(URL)
    dataframe.head()

    train, test = train_test_split(dataframe, test_size=0.2)
    train, val = train_test_split(train, test_size=0.2)
    print(len(train), 'train examples')
    print(len(val), 'validation examples')
    print(len(test), 'test examples')

    # A utility method to create a tf.data dataset from a Pandas Dataframe
    def df_to_dataset(dataframe, shuffle=True, batch_size=32):
        dataframe = dataframe.copy()
        labels = dataframe.pop('target')
        ds = tf.data.Dataset.from_tensor_slices((dict(dataframe), labels))
        if shuffle:
            ds = ds.shuffle(buffer_size=len(dataframe))
        ds = ds.batch(batch_size)
        return ds

    batch_size = 5  # A small batch sized is used for demonstration purposes
    train_ds = df_to_dataset(train, batch_size=batch_size)
    val_ds = df_to_dataset(val, shuffle=False, batch_size=batch_size)
    test_ds = df_to_dataset(test, shuffle=False, batch_size=batch_size)

    age = feature_column.numeric_column("age")

    feature_columns = []
    feature_layer_inputs = {}

    # numeric cols
    for header in ['age', 'trestbps', 'chol', 'thalach', 'oldpeak', 'slope', 'ca']:
        feature_columns.append(feature_column.numeric_column(header))
        feature_layer_inputs[header] = tf.keras.Input(shape=(1,), name=header)

    # bucketized cols
    age_buckets = feature_column.bucketized_column(age, boundaries=[18, 25, 30, 35, 40, 45, 50, 55, 60, 65])
    feature_columns.append(age_buckets)

    # indicator cols
    thal = feature_column.categorical_column_with_vocabulary_list(
        'thal', ['fixed', 'normal', 'reversible'])
    thal_one_hot = feature_column.indicator_column(thal)
    feature_columns.append(thal_one_hot)
    feature_layer_inputs['thal'] = tf.keras.Input(shape=(1,), name='thal', dtype=tf.string)

    # embedding cols
    thal_embedding = feature_column.embedding_column(thal, dimension=8)
    feature_columns.append(thal_embedding)

    # crossed cols
    crossed_feature = feature_column.crossed_column([age_buckets, thal], hash_bucket_size=1000)
    crossed_feature = feature_column.indicator_column(crossed_feature)
    feature_columns.append(crossed_feature)

    batch_size = 32
    train_ds = df_to_dataset(train, batch_size=batch_size)
    val_ds = df_to_dataset(val, shuffle=False, batch_size=batch_size)
    test_ds = df_to_dataset(test, shuffle=False, batch_size=batch_size)

    feature_layer = tf.keras.layers.DenseFeatures(feature_columns)
    feature_layer_outputs = feature_layer(feature_layer_inputs)
    x = layers.Dense(128, activation='relu')(feature_layer_outputs)
    x = layers.Dense(64, activation='relu')(x)
    baggage_pred = layers.Dense(1, activation='sigmoid')(x)

    model = keras.Model(inputs=[v for v in feature_layer_inputs.values()], outputs=baggage_pred)

    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    model.fit(train_ds)
    print("okkkkkk....")

def will_fail_can_delete():
    import pandas as pd
    # !pip install tensorflow==2.0.0-alpha0
    import tensorflow as tf
    from tensorflow import feature_column
    from tensorflow import keras
    from tensorflow.keras import layers
    from sklearn.model_selection import train_test_split

    URL = 'https://storage.googleapis.com/applied-dl/heart.csv'
    dataframe = pd.read_csv(URL)
    dataframe.head()

    train, test = train_test_split(dataframe, test_size=0.2)
    train, val = train_test_split(train, test_size=0.2)
    print(len(train), 'train examples')
    print(len(val), 'validation examples')
    print(len(test), 'test examples')

    # A utility method to create a tf.data dataset from a Pandas Dataframe
    def df_to_dataset(dataframe, shuffle=True, batch_size=32):
        dataframe = dataframe.copy()
        labels = dataframe.pop('target')
        ds = tf.data.Dataset.from_tensor_slices((dict(dataframe), labels))
        if shuffle:
            ds = ds.shuffle(buffer_size=len(dataframe))
        ds = ds.batch(batch_size)
        return ds

    batch_size = 5  # A small batch sized is used for demonstration purposes
    train_ds = df_to_dataset(train, batch_size=batch_size)
    val_ds = df_to_dataset(val, shuffle=False, batch_size=batch_size)
    test_ds = df_to_dataset(test, shuffle=False, batch_size=batch_size)

    age = feature_column.numeric_column("age")
    age_buckets = feature_column.bucketized_column(age, boundaries=[18, 25, 30, 35, 40, 45, 50, 55, 60, 65])
    thal = feature_column.categorical_column_with_vocabulary_list(
        'thal', ['fixed', 'normal', 'reversible'])
    thal_one_hot = feature_column.indicator_column(thal)
    thal_embedding = feature_column.embedding_column(thal, dimension=8)
    thal_hashed = feature_column.categorical_column_with_hash_bucket(
        'thal', hash_bucket_size=1000)
    crossed_feature = feature_column.crossed_column([age_buckets, thal], hash_bucket_size=1000)

    feature_columns = []

    # numeric cols
    for header in ['age', 'trestbps', 'chol', 'thalach', 'oldpeak', 'slope', 'ca']:
        feature_columns.append(feature_column.numeric_column(header))

    # bucketized cols
    age_buckets = feature_column.bucketized_column(age, boundaries=[18, 25, 30, 35, 40, 45, 50, 55, 60, 65])
    feature_columns.append(age_buckets)

    # indicator cols
    thal = feature_column.categorical_column_with_vocabulary_list(
        'thal', ['fixed', 'normal', 'reversible'])
    thal_one_hot = feature_column.indicator_column(thal)
    feature_columns.append(thal_one_hot)

    # embedding cols
    thal_embedding = feature_column.embedding_column(thal, dimension=8)
    feature_columns.append(thal_embedding)

    # crossed cols
    crossed_feature = feature_column.crossed_column([age_buckets, thal], hash_bucket_size=1000)
    crossed_feature = feature_column.indicator_column(crossed_feature)
    feature_columns.append(crossed_feature)

    batch_size = 32
    train_ds = df_to_dataset(train, batch_size=batch_size)
    val_ds = df_to_dataset(val, shuffle=False, batch_size=batch_size)
    test_ds = df_to_dataset(test, shuffle=False, batch_size=batch_size)

    feature_layer = tf.keras.layers.DenseFeatures(feature_columns)
    inputs = tf.keras.layers.Input(tensor=feature_layer, name='features')

    x = layers.Dense(128, activation='relu')(inputs)
    x = layers.Dense(64, activation='relu')(x)
    baggage_pred = layers.Dense(1, activation='sigmoid')(x)

    model = keras.Model(inputs=inputs, outputs=baggage_pred)

    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])


if __name__ == '__main__':
    run_keras_model()
    # nlp_ragged_tensor()
    # run_movielens_wide_deep_keras_model()
    # run_hst_recommend_system()
    # run_hst_recommend_system1()
    # run_hst_recommend_system2()
    # run_wine_wide_deep_keras_model()
    # result_is_ok_can_not_delete()
    # will_fail_not_need_delete() #一个例子, 如果从alpha0升级到tensorflow=2.0.0-beta1时会报错: tensorflow.python.framework.errors_impl.InvalidArgumentError:  You must feed a value for placeholder tensor 'child_gender_young'
    # keras_input_will_ok_no_need_delete()























