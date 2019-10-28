""" Zooper Vision AI FineTuner.

A library to fine tune vision model for specific task(s).

requirements:
    - tensorflow-gpu>=1.15.0
    - keras>=2.2.5

Copyright Zooper 2019.
"""
import json
import os
import time
import boto3

import tensorflow as tf

import math
import numpy as np

from datetime import datetime
from os.path import join, basename, splitext, isdir, exists

from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
from keras.models import Sequential, Input, Model, K
from keras.layers import Dropout, Flatten, Dense, Activation
from keras import applications, layers
from keras import optimizers
from keras import regularizers


from zooper_common.ai import ZooperInceptionResNetV2
from zooper_common.s3 import S3Utility
s3 = S3Utility()


class ZooperVisionFineTuner:
    """ Zooper's vision fine-tuner class.

    Quickstart:
    ===========

    z = ZooperVisionFineTuner(
        base_model_name='ZooperInceptionResNetV2',
        dense_layer_size=512,
        num_classes=8,
        storage_bucket='premium-handbags',
        train_data_dir='/tmp/premium_handbags/train',
        validation_data_dir='/tmp/premium_handbags/validation'
    )

    # Extract and save bottleneck features from the base model.
    z.extract_bottlebeck_features(
        bottleneck_feature_file_prefix='bottleneck_features')
    # Pretrain the top model.
    z.train_top_model(
        output_weights_path='201910261243.h5',
        epochs=14)

    """
    train_data_dir = '/tmp/train'
    validation_data_dir = '/tmp/validation'
    nb_train_samples = 2512
    nb_validation_samples = 608
    batch_size = 16
    use_tensorboard = False
    storage_bucket = 'zooper_models'

    def __init__(self,
            base_model_name='ZooperInceptionResNetV2',
            storage_bucket=None,
            input_image_width=224, input_image_height=224,
            dense_layer_size=512, num_classes=8,
            train_data_dir='/tmp/train', validation_data_dir='/tmp/validation'):
        # Assuming the TF layout.
        self.base_model_name = base_model_name
        self.dense_layer_size = dense_layer_size
        self.num_classes = num_classes
        self.input_image_width = input_image_width
        self.input_image_height = input_image_height
        self.input_shape = (input_image_width, input_image_height, 3)
        self.storage_bucket = storage_bucket
        self.train_data_dir = train_data_dir
        self.validation_data_dir = validation_data_dir

    @staticmethod
    def get_data_statistics(root_dir):
        image_dirs = [d for d in os.listdir(root_dir) if isdir(join(root_dir, d))]
        print(image_dirs)
        cat = {}
        total_count = 0
        for d in image_dirs:
            list_files = os.listdir(join(root_dir, d))
            count = len(list_files)
            cat[d] = count
            total_count += count
        print(json.dumps(cat, indent=2))
        print('total: {}'.format(total_count))
        return cat

    def get_labels(self, data_dir, stats=None):
        """ Get labels from the dataset, by scanning the data_dir and doing one-hot-encoding.
        """
        datagen = ImageDataGenerator(rescale=1. / 255)
        generator = datagen.flow_from_directory(
            data_dir,
            target_size=(self.input_image_height, self.input_image_width),
            batch_size=self.batch_size,
            class_mode='categorical',
            shuffle=False)
        print(generator.class_indices.keys())

        label_index = []
        prev_index = 0
        if stats is not None:
          for k, v in generator.class_indices.items():
            label_index.append(prev_index)
            prev_index += stats[k]
            print('{}:{}'.format(k, stats[k]))
        number_of_examples = len(generator.filenames)
        number_of_generator_calls = math.ceil(number_of_examples / (1.0 * self.batch_size))
        # 1.0 above is to skip integer division

        labels = []
        for i in range(0,int(number_of_generator_calls)):
            labels.extend(np.array(generator[i][1]))
        for idx in label_index:
          print(labels[idx])
        return np.array(labels)

    def extract_bottlebeck_features(self, bottleneck_feature_file_prefix='bottleneck_features'):
        """ Extract and save the base_model output as bottleneck features.

        The output bottleneck features can be used to pretrained a Dense layer.
        At the end of the process the features are written to:
            - `bottleneck_feature_file_prefix` + _train.npy
            - `bottleneck_feature_file_prefix` + _validation.npy
        """
        print('Extracting bottleneck features of {} model ...'.format(self.base_model_name))
        train_datagen = ImageDataGenerator(
            rescale=1. / 255,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
#           rotation_range=30,
#           width_shift_range=0.2,
#           height_shift_range=0.2,
#           fill_mode='nearest',
        )

        test_datagen = ImageDataGenerator(rescale=1. / 255)

        # Build the tower.
        model = self.create_base_model()

        generator = train_datagen.flow_from_directory(
            self.train_data_dir,
            target_size=(self.input_image_width, self.input_image_height),
            batch_size=self.batch_size,
            class_mode='categorical',
            shuffle=False,
        )
        bottleneck_features_train = model.predict_generator(
            generator, self.nb_train_samples // self.batch_size)
        np.save(open(bottleneck_feature_file_prefix + '_train.npy', 'wb'),
                bottleneck_features_train)

        generator = test_datagen.flow_from_directory(
            self.validation_data_dir,
            target_size=(self.input_image_width, self.input_image_height),
            batch_size=self.batch_size,
            class_mode='categorical',
            shuffle=False,
        )
        bottleneck_features_validation = model.predict_generator(
            generator, self.nb_validation_samples // self.batch_size)
        np.save(open(bottleneck_feature_file_prefix + '_validation.npy', 'wb'),
                bottleneck_features_validation)
        if self.storage_bucket is not None:
            s3.upload_folder(
                    bottleneck_feature_file_prefix + '_train.npy',
                    bucket=self.storage_bucket,
                    prefix=self.base_model_name)
            s3.upload_folder(
                    bottleneck_feature_file_prefix + '_validation.npy',
                    bucket=self.storage_bucket,
                    prefix=self.base_model_name)

    def train_top_model(self,
            output_weights_path,
            epochs=10,
            bottleneck_feature_file_prefix='bottleneck_features'):
        """ Training only the top Dense layers using the bottleneck features.
        """
        train_data = np.load(open(bottleneck_feature_file_prefix + '_train.npy', 'rb'))
        print(train_data.shape)
        stats = ZooperVisionFineTuner.get_data_statistics(self.train_data_dir)
        train_labels = self.get_labels(self.train_data_dir, stats)[:self.nb_train_samples]
        print(train_labels.shape)

        validation_data = np.load(open(bottleneck_feature_file_prefix + '_validation.npy', 'rb'))
        print(validation_data.shape)
        stats = ZooperVisionFineTuner.get_data_statistics(self.validation_data_dir)
        validation_labels = self.get_labels(self.validation_data_dir, stats)[:self.nb_validation_samples]
        print(validation_labels.shape)

        model = self.create_top_model(train_data.shape[1:])

        # Compile the model with a SGD/momentum optimizer
        # and a very slow learning rate.
        sgd = optimizers.SGD(lr=1e-4, momentum=0.9)
        model.compile(loss='categorical_crossentropy',
                      optimizer=sgd,
                      metrics=['accuracy'])

        try:
          timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
          if self.use_tensorboard:
            logdir = "logs/scalars/" + timestamp
            tensorboard_callback = keras.callbacks.TensorBoard(
                log_dir=logdir)

            training_history = model.fit(
                train_data,
                train_labels,
                epochs=epochs,
                batch_size=self.batch_size,
                validation_data=(validation_data, validation_labels),
                callbacks=[tensorboard_callback])
            print("Average test loss: ", np.average(
                training_history.history['loss']))
          else:
            model.fit(
                train_data,
                train_labels,
                epochs=epochs,
                batch_size=self.batch_size,
                validation_data=(validation_data, validation_labels))

          model.save_weights(output_weights_path)
          if self.storage_bucket is not None:
              print('Saving output weights {} ...'.format(output_weights_path))
              s3.upload_folder(output_weights_path,
                               bucket=self.storage_bucket,
                               prefix=self.base_model_name)
          print('Completed training.')
        except Exception as e:
          print(e)


    def create_top_model(self, input_shape,
                         enable_regularizer=True):
        """ Create dense (top) layer as Sequential. """
        base_model = Sequential()
        base_model.add(Flatten(input_shape=input_shape))
        if enable_regularizer:
            base_model.add(Dense(self.dense_layer_size,
                                 name='fc1_{}'.format(self.dense_layer_size),
                                 activation='relu',
                                 kernel_regularizer=regularizers.l2(0.005),
                                 bias_regularizer=regularizers.l2(0.005)))
            base_model.add(Dropout(0.5))
            base_model.add(Dense(self.dense_layer_size,
                                 name='fc2_{}'.format(self.dense_layer_size),
                                 activation='relu',
                                 kernel_regularizer=regularizers.l2(0.005),
                                 bias_regularizer=regularizers.l2(0.005)))
            base_model.add(Dropout(0.5))
            base_model.add(Dense(self.num_classes,
                                 name='fc3_{}'.format(self.num_classes),
                                 kernel_regularizer=regularizers.l2(0.005),
                                 bias_regularizer=regularizers.l2(0.005)))
            base_model.add(Activation('softmax'))
        else:
            base_model.add(Dense(self.dense_layer_size,
                                 name='fc1_{}'.format(self.dense_layer_size),
                                 activation='relu'))
            base_model.add(Dropout(0.5))
            base_model.add(Dense(self.dense_layer_size,
                                 name='fc2_{}'.format(self.dense_layer_size),
                                 activation='relu'))
            base_model.add(Dropout(0.5))
            base_model.add(Dense(self.num_classes,
                                 name='fc3_{}'.format(self.num_classes)))
            base_model.add(Activation('softmax'))
        return base_model

    def create_base_model(self, weights='imagenet'):
        """ Create base tower model. """
        print('Creating `{}` model ...'.format(self.base_model_name))
        if self.base_model_name == 'ZooperInceptionResNetV2':
            base_model = ZooperInceptionResNetV2(
                include_top=False,
                weights=weights,
                input_shape=self.input_shape,
                classes=self.num_classes,
            )
        elif self.base_model_name == 'InceptionResNetV2':
            base_model = applications.inception_resnet_v2.InceptionResNetV2(
                include_top=False,
                weights=weights,
                input_shape=self.input_shape,
                classes=self.num_classes,
            )
        elif self.base_model_name == 'VGG16':
            base_model = applications.VGG16(
                include_top=False,
                weights=weights,
                input_shape=self.input_shape,
                classes=self.num_classes,
            )
        elif self.base_model_name == 'VGG19':
            base_model = applications.VGG19(
                include_top=False,
                weights=weights,
                input_shape=self.input_shape,
                classes=self.num_classes,
            )
        elif self.base_model_name == 'ResNet50':
            base_model = applications.ResNet50(
                include_top=False,
                weights=weights,
                input_shape=self.input_shape,
                classes=self.num_classes,
            )
        elif self.base_model_name == 'InceptionV3':
            base_model = applications.inception_v3.InceptionV3(
                include_top=False,
                weights=weights,
                input_shape=self.input_shape,
                classes=self.num_classes,
            )
        elif self.base_model_name == 'DenseNet169':
            base_model = applications.densenet.DenseNet169(
                include_top=False,
                weights=weights,
                input_shape=self.input_shape,
                classes=self.num_classes,
            )
        elif self.base_model_name == 'MobileNet':
            base_model = applications.mobilenet.MobileNet(
                include_top=False,
                weights=weights,
                input_shape=self.input_shape,
                classes=self.num_classes,
            )
        elif self.base_model_name == 'MobileNetV2':
            base_model = applications.mobilenet_v2.MobileNetV2(
                include_top=False,
                weights=weights,
                input_shape=self.input_shape,
                classes=self.num_classes,
            )
        else:
            raise ValueError('Not supported model {}.'.format(self.base_model_name))
        return base_model

    def create_full_model(self,
                          weights_config={
                              "top_layer": False,
                              "path": None,
                          },
                          mode='training',
                          train_last_k_layers=3):
        """ Create full tower (base + dense). """
        st = time.time()
        input_tensor = Input(shape=self.input_shape)

        if mode == 'inference':
            print('[Inference mode]')
            K.set_learning_phase(0)
            # For inference, do not load 'imagenet' weights by default.
            base_model = self.create_base_model()
        elif mode == 'training':
            print('[Training mode]')
            base_model = self.create_base_model()
        else:
            raise ValueError('Invalid mode: {}'.format(mode))

        # Build a classifier model to put on top of the convolutional model.
        # Note that it is necessary to start with a fully-trained
        # classifier, including the top classifier,
        # in order to successfully do fine-tuning.
        top_model = self.create_top_model(base_model.output_shape[1:])
        pretrained_weights_path = weights_config['path']
        if (weights_config['top_layer']
            and pretrained_weights_path is not None):
            print('Loading top-level weights: {} ...'.format(
                pretrained_weights_path))
            top_model.load_weights(pretrained_weights_path)

        model = Model(inputs=base_model.input,
                      outputs=top_model(base_model.output))
        model.base_model = base_model

        if not weights_config['top_layer']:
            print('Loading full weights: {} ...'.format(
                pretrained_weights_path))
            model.load_weights(pretrained_weights_path)

        print('Model loaded.')
        print('|Layers|:{}'.format(len(model.layers)))

        # Set the base_model layers (up to the last 12th)
        # to non-trainable (weights will not be updated)
        if mode == 'training':
            print('Fine tuning last-{} layers ...'.format(train_last_k_layers))
            layers = model.layers[:-train_last_k_layers]
        elif mode == 'inference':
            layers = model.layers

        for layer in layers:
            layer.trainable = False
            # This is important for model with BN to work with fine-tuning.
            # References:
            # - https://github.com/keras-team/keras/pull/9965#issuecomment-382801648
            # - https://github.com/keras-team/keras/issues/9214#issuecomment-422490253
            if (layer.name.endswith('_bn')
                or layer.name.startswith('batch_normalization')):
                print('Freezing BN layers ... {}'.format(layer.name))
                layer.call(layer.input, training=False)

        # compile the model with a SGD/momentum optimizer
        # and a very slow learning rate.
        sgd = optimizers.SGD(lr=1e-4, momentum=0.9)
        model.compile(
                loss='categorical_crossentropy',
                optimizer=sgd,
                metrics=['accuracy'])
        print('{} model is loaded. Elapsed time: {} secs'.format(
              self.base_model_name,
              time.time() - st))
        return model

    def tune(self,
             weights_config,
             epochs=10,
             train_last_k_layers=3,
             steps_per_epoch=10000,
             validation_steps=1000):
        """ Fine tuning a pre-trained model. """
        timestamp = datetime.now().strftime("%Y%m%d-%H")
        pretrained_weights_path = weights_config['path']
        model = self.create_full_model(
            weights_config=weights_config,
            train_last_k_layers=train_last_k_layers,
            mode='training')
        filename, ext = os.path.splitext(pretrained_weights_path)
        output_weights=filename + '_finetuned_lastklayer{}_ep{}_{}{}'.format(
                train_last_k_layers, epochs, timestamp, ext)

        # Prepare data augmentation configuration
        # TODO(zooper): make this configurable.
        train_datagen = ImageDataGenerator(
            rotation_range=15,
            width_shift_range=0.2,
            height_shift_range=0.2,
            rescale=1. / 255,
            shear_range=0.2,
            zoom_range=[0.5,1.0],
            brightness_range=[0.5, 1.5],
            horizontal_flip=True)

        test_datagen = ImageDataGenerator(rescale=1. / 255)

        print('Initializing train_generator ...')
        train_generator = train_datagen.flow_from_directory(
            self.train_data_dir,
            target_size=(self.input_image_height, self.input_image_width),
            batch_size=self.batch_size,
            class_mode='categorical',
            shuffle=False)

        print('Initializing validation_generator ...')
        validation_generator = test_datagen.flow_from_directory(
            self.validation_data_dir,
            target_size=(self.input_image_height, self.input_image_width),
            batch_size=self.batch_size,
            class_mode='categorical',
            shuffle=False)

        model.summary()

        # Fine-tune the model.
        model.fit_generator(
            train_generator,
            steps_per_epoch=steps_per_epoch, #nb_train_samples // batch_size,
            epochs=epochs,
            validation_data=validation_generator,
            validation_steps=validation_steps) #nb_validation_samples // batch_size)

        model.save_weights(output_weights)
        if self.storage_bucket is not None:
            s3.upload_folder(output_weights, bucket=self.storage_bucket, prefix=self.base_model_name)
        print('Fine tuning is completed.')
