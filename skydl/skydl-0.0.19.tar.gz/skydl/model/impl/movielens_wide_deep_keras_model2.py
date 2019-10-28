# -*- coding: utf-8 -*-
import tensorflow as tf
import tensorflow_datasets as tfds
from tensorflow.python import keras
import numpy as np
from skydl.datasets.movielens_dataset_builder import MovieLensDatasetBuilder
from skydl.model.default_keras_model import DefaultKerasModel
from skydl.model.train_phase_enum import TrainPhaseEnum
from py_common_util.common.common_utils import CommonUtils
import sys,os
sys.path.append(os.path.abspath('%s/..' % sys.path[0]))


class MovieLensWideDeepKerasModel2(DefaultKerasModel):
    """
    https://www.curiousily.com/posts/heart-disease-prediction-in-tensorflow-2/
    Building a book Recommendation System using Keras  https://towardsdatascience.com/building-a-book-recommendation-system-using-keras-1fba34180699
    """
    def adjust_parse_args_value(self):
        super().adjust_parse_args_value()
        self.parser_args.data_path = sys.path[0] + '/../../dataset'
        self.parser_args.use_cuda = True
        self.parser_args.init_from_saver = True
        self.parser_args.train_phase = TrainPhaseEnum.Inference.value
        self.parser_args.model_version = '1'
        self.parser_args.epochs = 1
        self.parser_args.batch_size = 128
        self.parser_args.log_interval = 1000

    @CommonUtils.print_exec_time
    def load_data(self, *args, **kwargs):
        super().load_data(*args, **kwargs)
        dataset_name = MovieLensDatasetBuilder.camelcase_to_snakecase("MovieLensDatasetBuilder")
        num_examples = MovieLensDatasetBuilder.get_num_examples(dataset_name)
        full_datasets = MovieLensDatasetBuilder.load_batched_datasets(dataset_name,
                                                                      split=[tfds.Split.TRAIN],
                                                                      batch_size=128,
                                                                      epochs=1)
        batched_train_dataset, batched_validation_dataset, batched_evaluate_dataset = MovieLensDatasetBuilder.split_full_datasets(full_datasets,
                                                                                                      num_examples=MovieLensDatasetBuilder.get_total_num_batch(
                                                                                                          num_examples,
                                                                                                          128),
                                                                                                      train_size=0.7,
                                                                                                      validation_size=0,
                                                                                                      test_size=0.2)
        np_user_ids = np.array([])
        np_item_ids = np.array([])
        np_labels = np.array([])
        if self.is_inference_phase():
            # get 2 batched test_dataset: i.e. 128 * 3
            stat_dataset = batched_evaluate_dataset.take(3)
        else:
            # get train_dataset
            stat_dataset = batched_train_dataset
        for features, labels in MovieLensDatasetBuilder.read_batched_datasets(stat_dataset):
            np_user_ids = np.append(np_user_ids, features['user_id'])
            np_item_ids = np.append(np_item_ids, features['item_id'])
            np_labels = np.append(np_labels, labels)
        return batched_train_dataset, batched_validation_dataset, batched_evaluate_dataset, np_user_ids, np_item_ids, np_labels

    def fit_ok(self, *args, **kwargs):
        """可以成功运行"""
        if not self.is_training_phase():
            return self
        train_dataset, validation_dataset, test_dataset, np_user_ids, np_item_ids, np_labels = self.load_data()
        user_feature_column = MovieLensDatasetBuilder.build_numeric_feature_columns(["user_id"])
        item_feature_column = MovieLensDatasetBuilder.build_numeric_feature_columns(["item_id"])
        total_items = len(np.unique(np_item_ids))
        total_users = len(np.unique(np_user_ids))

        # creating user embedding path
        user_input = keras.Input(shape=[1], name="User-Input")
        user_embedding = keras.layers.Embedding(total_users, 10, name="User-Embedding")(user_input)
        user_vec = keras.layers.Flatten(name="Flatten-Users")(user_embedding)

        # creating book embedding path
        book_input = keras.Input(shape=[1], name="Book-Input")
        book_embedding = keras.layers.Embedding(total_items, 10, name="Book-Embedding")(book_input)
        book_vec = keras.layers.Flatten(name="Flatten-Books")(book_embedding)

        # performing dot product and creating model
        prod = keras.layers.Dot(name="Dot-Product", axes=1)([book_vec, user_vec])
        model = keras.Model([user_input, book_input], prod)
        model.compile('adam', 'mean_squared_error', ["accuracy"])
        model.fit([np_user_ids] + [np_item_ids], np_labels)
        model.summary()
        return self

    @CommonUtils.print_exec_time
    def fit(self, *args, **kwargs):
        if not self.is_training_phase():
            return self
        loaded_dataset = kwargs.get("loaded_dataset")
        if loaded_dataset is not None:
            batched_train_dataset = loaded_dataset[0]
            batched_evaluate_dataset = loaded_dataset[2]
            self.model.get_proxy().fit(batched_train_dataset, epochs=self.parser_args.epochs, callbacks=self.fit_callbacks())
            self.model.get_proxy().summary()
            # evaluate mode
            self.evaluate(batched_evaluate_dataset)
            # save model for tf serving
            self.save_model(batched_evaluate_dataset=batched_evaluate_dataset)

        # change to inference phase
        self.parser_args.train_phase = TrainPhaseEnum.Inference.value
        return self

    @CommonUtils.print_exec_time
    def evaluate(self, *args, **kwargs):
        test_loss, test_acc = self.model.get_proxy().evaluate(args[0])
        self.model.get_proxy().summary()
        print('\nTest accuracy:', test_acc)
        return self

    @CommonUtils.print_exec_time
    def save_model(self, *args, **kwargs):
        """save model for tf serving"""
        if not self.is_training_phase():
            return self
        # restore weights from latest checkpoint
        latest_checkpoint = tf.train.latest_checkpoint(self.get_model_checkpoint_dir())
        if latest_checkpoint:
            self.model.get_proxy().load_weights(latest_checkpoint)
            self.log.info("already called load_weights from: " + latest_checkpoint)
        saved_serving_path = self.parser_args.model_checkpoint_path + "/serving/models/" + self.model.name() + "/" + self.parser_args.model_version

        batched_evaluate_dataset = kwargs.get("batched_evaluate_dataset")
        # save model for tf serving
        if not self.model.get_proxy().inputs and batched_evaluate_dataset is not None:
            for batched_examples in tfds.as_numpy(batched_evaluate_dataset.take(1)):
                test_batched_features, test_batched_labels = batched_examples
                self.model.get_proxy()._set_inputs(test_batched_features)
        tf.saved_model.save(self.model.get_proxy(), saved_serving_path)
        self.log.info("already called saved_model to saved_serving_path: " + saved_serving_path)
        return self

    @CommonUtils.print_exec_time
    def serving(self, *args, **kwargs):
        if not self.is_inference_phase():
            return self
        # restore weights from latest checkpoint
        latest_checkpoint = tf.train.latest_checkpoint(self.get_model_checkpoint_dir())
        if latest_checkpoint:
            self.model.get_proxy().load_weights(latest_checkpoint)
            self.log.info("already called load_weights from: " + latest_checkpoint)
        saved_serving_path = self.parser_args.model_checkpoint_path + "/serving/models/" + self.model.name() + "/" + self.parser_args.model_version

        _, _, evaluate_dataset, np_user_ids, np_item_ids, np_labels = self.load_data()

        # predict
        self.predict(user_id=np_user_ids[2], np_item_ids=np_item_ids)

        # save model for tf serving
        if not self.model.get_proxy().inputs:
            for batched_examples in tfds.as_numpy(evaluate_dataset.take(1)):
                test_batched_features, test_batched_labels = batched_examples
                self.model.get_proxy()._set_inputs(test_batched_features)
        tf.saved_model.save(self.model.get_proxy(), saved_serving_path)
        return self

    @CommonUtils.print_exec_time
    def predict(self, *args, **kwargs):
        """python版的预测接口，返回预测结果"""
        if not self.is_inference_phase():
            return None
        user_id = kwargs.get("user_id")
        np_item_ids = kwargs.get("np_item_ids")

        users = np.array([user_id for i in range(len(np_item_ids))])
        predictions = self.model.get_proxy().predict([users, np_item_ids])
        predictions = np.array([a[0] for a in predictions])
        recommended_book_ids = (-predictions).argsort()
        print("用户Id：", int(user_id))
        print("推荐的新闻Id列表,Top(" + str(len(np_item_ids)) + ")：", recommended_book_ids)
        print("推荐得分倒序：", predictions[recommended_book_ids])
        return None

    @CommonUtils.print_exec_time
    def inference(self, tfx_host_port="http://localhost:8501/",model_name=None, features_list=[]):
        """
        TODO 该方法将被废弃，用predict方法替代
        inference request to tf serving
        https://medium.com/tensorflow/serving-ml-quickly-with-tensorflow-serving-and-docker-7df7094aa008
        #########################################
        $docker rmi -f <<old serving images>>
        $docker pull tensorflow/serving:1.13.0
        $docker run -p 8500:8500 -p 8501:8501 \
        --mount type=bind,source=/Users/tony/myfiles/spark/share/python-projects/deep_trading/skydl/examples/saved_model/serving/models/default_keras_net,target=/models/my_keras_model \
        -e MODEL_NAME=my_keras_model -t tensorflow/serving:1.13.0
        #########################################
        :param tfx_host_port: docker serving url, e.g. "http://localhost:8501/" 完整的post url，如"http://localhost:8501/v1/models/my_keras_model:predict"
        :param model_name: inference_model.model.name() e.g. "my_keras_model"
        :param features_list:  shape e.g. (1,28,28), 数据格式：tf_dataset_batched_features.tolist()[:100]
        features_list数据可以来自如下：
        _, evaluate_dataset = inference_model.load_data()
        import tensorflow_datasets as tfds
        for dataset in tfds.as_numpy(evaluate_dataset):
            features, labels = dataset
        features_list = features.tolist()
        :return:
        """
        import json
        import numpy
        import requests
        import traceback
        data = json.dumps({"signature_name": "serving_default",
                           "instances": features_list})
        headers = {"content-type": "application/json"}
        # 去掉url里最后一个/字符
        if tfx_host_port[-1] == '/':
            tfx_host_port = tfx_host_port[:-1]
        post_url = tfx_host_port + "/v1/models/" + model_name + ":predict"
        json_response = requests.post(post_url, data=data, headers=headers)
        print("the inference request takes times(milliseconds): " + str(json_response.elapsed.total_seconds()*1000))
        try:
            if not json_response.ok:
                self.log.info("the inference request failure, url: " + json_response.url + ", response code: " + str(json_response.status_code) + ", error reason: " + json_response.text)
                return []
            prediction_list = numpy.array(json_response.json()["predictions"])
            print("response is ok, prediction_list after argmax is:" + str(tf.argmax(prediction_list, axis=1).numpy()))
            return prediction_list
        except:
            print("exception occured at an inference request!")
            traceback.print_exc()
        return []
