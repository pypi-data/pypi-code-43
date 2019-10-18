"""
File that contains methods use to fit the data to the model and train it.
"""

from deepcinac.cinac_movie_patch import MoviePatchGeneratorMaskedVersions
from keras.utils import get_custom_objects, multi_gpu_model
import tensorflow as tf
import numpy as np
from datetime import time
import keras
from keras.layers import Conv2D, MaxPooling2D, Flatten, Bidirectional, BatchNormalization
from keras.layers import Input, LSTM, Dense, TimeDistributed, Activation, Lambda, Permute, RepeatVector
from keras.models import Model, Sequential
from keras.models import model_from_json
from keras.optimizers import RMSprop, adam, SGD
from keras import layers
from keras.callbacks import ReduceLROnPlateau, ModelCheckpoint, EarlyStopping
from keras import backend as K


def attention_3d_block(inputs, time_steps, use_single_attention_vector=False):
    """
    from: https://github.com/philipperemy/keras-attention-mechanism
    :param inputs:
    :param use_single_attention_vector:  if True, the attention vector is shared across
    the input_dimensions where the attention is applied.
    :return:
    """
    # inputs.shape = (batch_size, time_steps, input_dim)
    # print(f"inputs.shape {inputs.shape}")
    input_dim = int(inputs.shape[2])
    a = Permute((2, 1))(inputs)
    # a = Reshape((input_dim, time_steps))(a)  # this line is not useful. It's just to know which dimension is what.
    a = Dense(time_steps, activation='softmax')(a)
    if use_single_attention_vector:
        a = Lambda(lambda x: K.mean(x, axis=1))(a)  # , name='dim_reduction'
        a = RepeatVector(input_dim)(a)
    a_probs = Permute((2, 1))(a)  # , name='attention_vec'
    output_attention_mul = keras.layers.multiply([inputs, a_probs])
    return output_attention_mul

# ------------------------------------------------------------
# needs to be defined as activation class otherwise error
# AttributeError: 'Activation' object has no attribute '__name__'
# From: https://github.com/keras-team/keras/issues/8716
class Swish(Activation):

    def __init__(self, activation, **kwargs):
        super(Swish, self).__init__(activation, **kwargs)
        self.__name__ = 'swish'


def swish(x):
    """
    Implementing a the swish activation function.
    From: https://www.kaggle.com/shahariar/keras-swish-activation-acc-0-996-top-7
    Paper describing swish: https://arxiv.org/abs/1710.05941

    :param x:
    :return:
    """
    return K.sigmoid(x) * x
    # return Lambda(lambda a: K.sigmoid(a) * a)(x)

class CinacModel:

    def __init__(self, **kwargs):
        # TODO: Describe each argument
        self.n_gpus = kwargs.get("n_gpus", 1)
        self.using_multi_class = kwargs.get("using_multi_class", 1)  # 1 or 3 so far
        if self.using_multi_class not in [1, 3]:
            raise Exception(f"using_multi_class can take only 1 or 3 as value. "
                            f"Value passed being {self.using_multi_class}")

        self.n_epochs = kwargs.get("n_epochs", 30)
        # multiplying by the number of gpus used as batches will be distributed to each GPU
        self.batch_size = kwargs.get("batch_size", 8) * self.n_gpus

        self.window_len = kwargs.get("window_len", 100)
        self.max_width = kwargs.get("max_width", 25)
        self.max_height = kwargs.get("max_height", 25)
        self.max_n_transformations = kwargs.get("max_n_transformations", 6)  # TODO: 6
        self.pixels_around = kwargs.get("pixels_around", 0)
        self.with_augmentation_for_training_data = kwargs.get("with_augmentation_for_training_data", True)
        self.buffer = kwargs.get("buffer", 1)
        # between training, validation and test data
        self.split_values = kwargs.get("split_values", (0.8, 0.2, 0))
        if self.using_multi_class > 1:
            self.loss_fct = 'categorical_crossentropy'
        else:
            self.loss_fct = 'binary_crossentropy'
        self.with_learning_rate_reduction = kwargs.get("with_learning_rate_reduction", True)
        self.learning_rate_reduction_patience = kwargs.get("learning_rate_reduction_patience", 2)

        # ---------------------------
        # Model related (used to build the model)
        # ---------------------------
        self.overlap_value = kwargs.get("overlap_value", 0.9)  # TODO: 0.9
        self.dropout_value = kwargs.get("dropout_value", 0.5)
        self.dropout_value_rnn = kwargs.get("dropout_value_rnn", 0.5)
        self.dropout_at_the_end = kwargs.get("dropout_at_the_end", 0)
        self.with_batch_normalization = kwargs.get("with_batch_normalization", False)
        self.optimizer_choice = kwargs.get("optimizer_choice", "RMSprop")  # "SGD"  used to be "RMSprop"  "adam", SGD
        self.activation_fct = kwargs.get("activation_fct", "swish")
        self.without_bidirectional = kwargs.get("without_bidirectional", False)
        # TODO: try 256, 256, 256
        self.lstm_layers_size = kwargs.get("lstm_layers_size", (128, 256)) # TODO: 128, 256 # 128, 256, 512
        self.bin_lstm_size = kwargs.get("bin_lstm_size", 256)
        self.use_bin_at_al_version = kwargs.get("use_bin_at_al_version", True)  # TODO: True
        self.apply_attention = kwargs.get("apply_attention", True)  # TODO: True
        self.apply_attention_before_lstm = kwargs.get("apply_attention_before_lstm", True)
        self.use_single_attention_vector = kwargs.get("use_single_attention_vector", False)

        self.with_early_stopping = kwargs.get("with_early_stopping", True)
        self.early_stop_patience = kwargs.get("early_stop_patience", 15)  # 10
        self.model_descr = kwargs.get("model_descr", "")
        self.with_shuffling = kwargs.get("with_shuffling", True)
        self.seed_value = kwargs.get("seed_value", 42)  # use None to not use seed
        # main_ratio_balance = (0.6, 0.2, 0.2)
        self.main_ratio_balance = kwargs.get("main_ratio_balance", (0.7, 0.2, 0.1))
        self.crop_non_crop_ratio_balance = kwargs.get("crop_non_crop_ratio_balance", (-1, -1)) # (0.8, 0.2)
        self.non_crop_ratio_balance = kwargs.get("non_crop_ratio_balance", (-1, -1))  # (0.85, 0.15)
        # Maximum number of processes to spin up when using process-based threading
        self.workers = kwargs.get("workers", 10)

        self.results_path = kwargs.get("results_path", None)
        if self.results_path is None:
            raise Exception("You must set a results_path to indicate where to save the network files")

        # will be set in self.prepare_model()
        self.parallel_model = None

        self.movie_patch_generator = \
            MoviePatchGeneratorMaskedVersions(window_len=self.window_len, max_width=self.max_width,
                                              max_height=self.max_height,
                                              pixels_around=self.pixels_around,
                                              buffer=self.buffer, with_neuropil_mask=True,
                                              using_multi_class=self.using_multi_class)


    def add_input_data(self, cinac_recording, cell, frames_to_add, ground_truth, doubtful_frames, cells_to_remove):
        """
        Add input data.
        Args:
            cinac_recording: Represents the movie and cell's coord
            cell: cell index, corresponding to indexing in cinac_recording
            frames_to_add: 1d array, frames indices to take into consideration,
            same length as ground_truth and doubtful_frames
            ground_truth: 1d array, binary, 1 if the cell is active at a given frame, 0 otherwise,
            same length as frames_to_add and doubtful_frames
            doubtful_frames: 1d array, boolean, True, if the frame is doubtful, False otherwise.
            If the frame is doubtful, it means it won't be added as input
            same length as frames_to_add and raster_dur
            cells_to_remove:

        Returns:

        """
        pass

    def __build_model(self):
        """

        Returns:

        """

        """
        Attributes used:
        :param input_shape:
        :param lstm_layers_size:
        :param n_inputs:
        :param using_multi_class:
        :param bin_lstm_size:
        :param activation_fct:
        :param dropout_at_the_end: From Li et al. 2018 to avoid disharmony between batch normalization and dropout,
        if batch is True, then we should add dropout only on the last step before the sigmoid or softmax activation
        :param dropout_rate:
        :param dropout_rnn_rate:
        :param without_bidirectional:
        :param with_batch_normalization:
        :param apply_attention:
        :param apply_attention_before_lstm:
        :param use_single_attention_vector:
        :param use_bin_at_al_version:
        :return:
        """

        # n_frames represent the time-steps
        n_frames = self.input_shape[0]

        ##########################################################################
        #######################" VISION MODEL ####################################
        ##########################################################################
        # First, let's define a vision model using a Sequential model.
        # This model will encode an image into a vector.
        # TODO: Try dilated CNN
        # VGG-like convnet model
        vision_model = Sequential()
        get_custom_objects().update({'swish': Swish(swish)})
        # to choose between swish and relu

        # TODO: Try dilation_rate=2 argument for Conv2D
        # TODO: Try changing the number of filters like 32 and then 64 (instead of 64 -> 128)
        vision_model.add(Conv2D(64, (3, 3), padding='same', input_shape=self.input_shape[1:]))
        if self.activation_fct != "swish":
            vision_model.add(Activation(self.activation_fct))
        else:
            vision_model.add(Lambda(swish))
        if self.with_batch_normalization:
            vision_model.add(BatchNormalization())
        vision_model.add(Conv2D(64, (3, 3)))
        if self.activation_fct != "swish":
            vision_model.add(Activation(self.activation_fct))
        else:
            vision_model.add(Lambda(swish))
        if self.with_batch_normalization:
            vision_model.add(BatchNormalization())
        # TODO: trying AveragePooling
        vision_model.add(MaxPooling2D((2, 2)))

        vision_model.add(Conv2D(128, (3, 3), padding='same'))
        if self.activation_fct != "swish":
            vision_model.add(Activation(self.activation_fct))
        else:
            vision_model.add(Lambda(swish))
        vision_model.add(Conv2D(128, (3, 3)))
        if self.activation_fct != "swish":
            vision_model.add(Activation(self.activation_fct))
        else:
            vision_model.add(Lambda(swish))
        if self.with_batch_normalization:
            vision_model.add(BatchNormalization())
        vision_model.add(MaxPooling2D((2, 2)))

        # vision_model.add(Conv2D(256, (3, 3), activation=activation_fct, padding='same'))
        # vision_model.add(Conv2D(256, (3, 3), activation=activation_fct))
        # vision_model.add(Conv2D(256, (3, 3), activation=activation_fct))
        # vision_model.add(MaxPooling2D((2, 2)))
        # TODO: see to add Dense layer with Activation
        vision_model.add(Flatten())
        # size 2048
        # vision_model.add(Dense(2048))
        # if activation_fct != "swish":
        #     vision_model.add(Activation(activation_fct))
        # else:
        #     vision_model.add(Lambda(swish))
        # vision_model.add(Dense(2048))
        # if activation_fct != "swish":
        #     vision_model.add(Activation(activation_fct))
        # else:
        #     vision_model.add(Lambda(swish))

        if self.dropout_rate > 0:
            vision_model.add(layers.Dropout(self.dropout_rate))

        ##########################################################################
        # ######################" END VISION MODEL ################################
        ##########################################################################

        ##########################################################################
        # ############################## BD LSTM ##################################
        ##########################################################################
        # inputs are the original movie patches
        inputs = []
        # encoded inputs are the outputs of each encoded inputs after BD LSTM
        encoded_inputs = []

        for input_index in np.arange(self.n_inputs):
            video_input = Input(shape=self.input_shape, name=f"input_{input_index}")
            inputs.append(video_input)
            # This is our video encoded via the previously trained vision_model (weights are reused)
            encoded_frame_sequence = TimeDistributed(vision_model)(video_input)  # the output will be a sequence of vectors

            if self.apply_attention and self.apply_attention_before_lstm:
                # adding attention mechanism
                encoded_frame_sequence = attention_3d_block(inputs=encoded_frame_sequence, time_steps=n_frames,
                                                            use_single_attention_vector=self.use_single_attention_vector)

            for lstm_index, lstm_size in enumerate(self.lstm_layers_size):
                if lstm_index == 0:
                    rnn_input = encoded_frame_sequence
                else:
                    rnn_input = encoded_video

                return_sequences = True
                # if apply_attention and (not apply_attention_before_lstm):
                #     return_sequences = True
                # elif use_bin_at_al_version:
                #     return_sequences = True
                # elif using_multi_class <= 1:
                #     return_sequences = (lstm_index < (len(lstm_layers_size) - 1))
                # else:
                #     return_sequences = True
                if self.without_bidirectional:
                    encoded_video = LSTM(lstm_size, dropout=self.dropout_rnn_rate,
                                         recurrent_dropout=self.dropout_rnn_rate,
                                         return_sequences=return_sequences)(rnn_input)
                    # From Bin et al. test adding merging LSTM results + CNN representation then attention
                    if self.use_bin_at_al_version:
                        encoded_video = layers.concatenate([encoded_video, encoded_frame_sequence])
                else:
                    # there was a bug here, recurrent_dropout was taking return_sequences as value
                    encoded_video = Bidirectional(LSTM(lstm_size, dropout=self.dropout_rnn_rate,
                                                       recurrent_dropout=self.dropout_rnn_rate,
                                                       return_sequences=return_sequences), merge_mode='concat', )(rnn_input)
                    # From Bin et al. test adding merging LSTM results + CNN represnetation then attention
                    if self.use_bin_at_al_version:
                        encoded_video = layers.concatenate([encoded_video, encoded_frame_sequence])

            # TODO: test if GlobalMaxPool1D +/- dropout is useful here ?
            # encoded_video = GlobalMaxPool1D()(encoded_video)
            # encoded_video = Dropout(0.25)(encoded_video)
            # We can either apply attention a the end of each LSTM, or do it after the concatenation of all of them
            # it's the same if there is only one encoded_input
            # if apply_attention and (not apply_attention_before_lstm):
            #     # adding attention mechanism
            #     encoded_video = attention_3d_block(inputs=encoded_video, time_steps=n_frames,
            #                                        use_single_attention_vector=use_single_attention_vector)
            #     if using_multi_class <= 1:
            #         encoded_video = Flatten()(encoded_video)
            encoded_inputs.append(encoded_video)

        if len(encoded_inputs) == 1:
            merged = encoded_inputs[0]
        else:
            # TODO: try layers.Average instead of concatenate
            merged = layers.concatenate(encoded_inputs)
        # From Bin et al. test adding a LSTM here that will take merged as inputs + CNN represnetation (as attention)
        # Return sequences will have to be True and activate the CNN representation
        if self.use_bin_at_al_version:
            # next lines commented, seems like it didn't help at all
            # if with_batch_normalization:
            #     merged = BatchNormalization()(merged)
            # if dropout_rate > 0:
            #     merged = layers.Dropout(dropout_rate)(merged)

            merged = LSTM(self.bin_lstm_size, dropout=self.dropout_rnn_rate,
                          recurrent_dropout=self.dropout_rnn_rate,
                          return_sequences=True)(merged)
            print(f"merged.shape {merged.shape}")
            if self.apply_attention and (not self.apply_attention_before_lstm):
                # adding attention mechanism
                merged = attention_3d_block(inputs=merged, time_steps=n_frames,
                                            use_single_attention_vector=self.use_single_attention_vector)
            if self.using_multi_class <= 1:
                merged = Flatten()(merged)

        # TODO: test those 7 lines (https://www.kaggle.com/amansrivastava/exploration-bi-lstm-model)
        # number_dense_units = 1024
        # merged = Dense(number_dense_units)(merged)
        # merged = Activation(activation_fct)(merged)
        if self.with_batch_normalization:
            merged = BatchNormalization()(merged)
        if self.dropout_rate > 0:
            merged = (layers.Dropout(self.dropout_rate))(merged)
        elif self.dropout_at_the_end > 0:
            merged = (layers.Dropout(self.dropout_at_the_end))(merged)

        # if we use TimeDistributed then we need to return_sequences during the last LSTM
        if self.using_multi_class <= 1:
            # if use_bin_at_al_version:
            #     outputs = TimeDistributed(Dense(1, activation='sigmoid'))(merged)
            # else:
            outputs = Dense(n_frames, activation='sigmoid')(merged)
            # outputs = TimeDistributed(Dense(1, activation='sigmoid'))(merged)
        else:
            outputs = TimeDistributed(Dense(self.using_multi_class, activation='softmax'))(merged)
        if len(inputs) == 1:
            print(f"len(inputs) {len(inputs)}")
            inputs = inputs[0]

        print("Creating Model instance")
        video_model = Model(inputs=inputs, outputs=outputs)
        print("After Creating Model instance")

        return video_model

    def prepare_model(self):
        """
        Will build the model that will be use to fit the data.
        Should be called only after the data has been set.
        Returns:

        """

        # first building the generator that will allow the generate the data for each batch during network iterations
        params_generator = {
            'batch_size': self.batch_size,
            'window_len': self.window_len,
            'max_width': self.max_width,
            'max_height': self.max_height,
            'pixels_around': self.pixels_around,
            'buffer': self.buffer,
            'is_shuffle': True}

        # TODO: build DataGenerator
        training_generator = DataGenerator(self.train_data_list,
                                           with_augmentation=self.with_augmentation_for_training_data,
                                           movie_patch_generator=self.movie_patch_generator,
                                           **params_generator)
        validation_generator = DataGenerator(self.valid_data_list, with_augmentation=False,
                                             movie_patch_generator=self.movie_patch_generator,
                                             **params_generator)

        self.input_shape = training_generator.input_shape

        if self.input_shape is None:
            raise Exception("prepare_model() cannot be called before the data has been provided to the model")
        if self.n_gpus == 1:
            print("Building the model on 1 GPU")
            model = self.__build_model()
        else:
            print(f"Building the model on {self.n_gpus} GPU")
            # We recommend doing this with under a CPU device scope,
            # so that the model's weights are hosted on CPU memory.
            # Otherwise they may end up hosted on a GPU, which would
            # complicate weight sharing.
            # https://www.tensorflow.org/api_docs/python/tf/keras/utils/multi_gpu_model
            with tf.device('/cpu:0'):
                model = self.__build_model()
        print(model.summary())

        if self.n_gpus > 1:
            self.parallel_model = multi_gpu_model(model, gpus=self.n_gpus)
        else:
            self.parallel_model = model

        # Save the model architecture
        with open(f'{self.results_path}/transient_classifier_model_architecture_{self.model_descr}.json', 'w') as f:
            f.write(model.to_json())

    def fit(self):
        # Train model on dataset
        start_time = time.time()

        history = self.parallel_model.fit_generator(generator=self.training_generator,
                                                    validation_data=self.validation_generator,
                                                    epochs=self.n_epochs,
                                                    use_multiprocessing=True,
                                                    workers=self.workers,
                                                    callbacks=self.callbacks_list, verbose=2)  # TODO: Verbose=2

        print(f"history.history.keys() {history.history.keys()}")
        stop_time = time.time()
        print(f"Time for fitting the model to the data with {self.n_epochs} epochs: "
              f"{np.round(stop_time - start_time, 3)} s")

        history_dict = history.history
        # TODO: save parameters used + metrics for each epochs
