# -*- coding: utf-8 -*-
import tensorflow as tf
from tensorflow import keras


class KerasFeatureInputMergedModel(keras.Model):
    """
    keras多输入多输出设计: 合并几个模型一起训练
    注意：如果从tensorflow-2.0.0alpha0升级到tensorflow=2.0.0-beta1时会报错: tensorflow.python.framework.errors_impl.InvalidArgumentError:  You must feed a value for placeholder tensor 'child_gender_young'
    work around for issue: Unable to use FeatureColumn with Keras Functional API #27416  https://github.com/tensorflow/tensorflow/issues/27416
    https://www.curiousily.com/posts/heart-disease-prediction-in-tensorflow-2/
    ```
    import pandas as pd
    from tensorflow import feature_column
    from tensorflow import keras

    feature_columns = []
    child_month_young = feature_column.numeric_column("child_month_young")
    kid_age_youngest_buckets = feature_column.bucketized_column(child_month_young, boundaries=[0, 12, 24, 36, 72, 96])
    feature_columns.append(kid_age_youngest_buckets)

    child_gender_young = feature_column.categorical_column_with_vocabulary_list(
        'child_gender_young', ['boy', 'girl', ''])
    child_gender_young_one_hot = feature_column.indicator_column(child_gender_young)
    feature_columns.append(child_gender_young_one_hot)

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
    #######################################
    # model.save("/tmp/saved_model/xxx.h5")
    # model.load_weights("/tmp/saved_model/xxx.h5")
    ```
    """
    def __init__(self, *args, **kwargs):
        keras_feature_columns = kwargs.pop('feature_columns', [])
        keras_feature_column_names = kwargs.pop('feature_column_names', [])
        super().__init__(*args, **kwargs)
        self.keras_feature_columns = keras_feature_columns
        self.keras_feature_column_names = keras_feature_column_names

    def call(self, inputs, training=False):
        from tensorflow.python.keras.engine import training_utils
        feature_input_items = {k: v for k, v in inputs.items() if k in self.keras_feature_column_names}
        self.feature_inputs = training_utils.ModelInputs(feature_input_items).get_symbolic_inputs()
        return tf.keras.layers.DenseFeatures(self.keras_feature_columns)(inputs)

    @staticmethod
    def build_keras_feature_column_output_layer(one_length_train_dataset, feature_columns, feature_column_names):
        feature_model = KerasFeatureInputMergedModel(feature_columns=feature_columns, feature_column_names=feature_column_names)
        feature_model.compile(optimizer='adam', loss='binary_crossentropy')
        feature_model.fit(one_length_train_dataset, epochs=1)
        fitted_feature_inputs = feature_model.feature_inputs

        keras_pure_input_layer_dict = {}
        for name, tensor in fitted_feature_inputs.items():
            keras_pure_input_layer = keras.layers.Input(shape=tensor.shape, name=name, tensor=tensor)
            keras_pure_input_layer_dict[name] = keras_pure_input_layer
        return tf.keras.layers.DenseFeatures(feature_columns)(keras_pure_input_layer_dict), keras_pure_input_layer_dict

