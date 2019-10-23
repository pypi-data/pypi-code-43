import os

import numpy as np
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from tqdm import tqdm

from .models.tagger_model import TaggerModel

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


class TFTagger:
    def __init__(self, embedding_size=300, batch_size=32, epoch=100):
        self.embedding_size = embedding_size
        self.batch_size = batch_size
        self.epoch = epoch
        self.model = None

    def build_model(self):
        return TaggerModel(embedding_size=self.embedding_size,
                           vocab_size=self.vocab_size,
                           tag_size=self.label_size)

    def fit(self, X, y):
        """Model training."""
        tokenizer = tf.keras.preprocessing.text.Tokenizer(char_level=True)
        tokenizer.fit_on_texts(X)
        vocab_size = len(tokenizer.index_word) + 1

        label = LabelEncoder()
        tags = []
        for yy in y:
            tags += yy
        label.fit(['<PAD>'] + tags)
        label_size = len(label.classes_)
        assert label_size >= 2

        self.vocab_size = vocab_size
        self.label_size = label_size
        if self.model is None:
            model = self.build_model()
        else:
            model = self.model

        optimizer = tf.keras.optimizers.Adam()

        X_len = [len(x) for x in X]
        X_vec = tf.keras.preprocessing.sequence.pad_sequences(
            tokenizer.texts_to_sequences(X), padding='post')
        max_length = X_vec.shape[1]
        y_vec = np.array([
            label.transform(yy + ['<PAD>'] * (max_length - len(yy)))
            for yy in y
        ])

        total_batch = int(np.ceil(len(X_vec) / self.batch_size))
        for i_epoch in range(self.epoch):
            pbar = tqdm(range(total_batch), ncols=10)
            pbar.set_description(f'epoch: {i_epoch} loss: /')
            for i in pbar:
                i_min = i * self.batch_size
                i_max = min((i + 1) * self.batch_size, len(X_vec))
                x = X_vec[i_min:i_max]
                xl = X_len[i_min:i_max]
                tags = y_vec[i_min:i_max]
                x = tf.convert_to_tensor(x, dtype=tf.float32)
                xl = tf.convert_to_tensor(xl, dtype=tf.int32)
                tags = tf.convert_to_tensor(tags, dtype=tf.int32)
                with tf.GradientTape() as tape:
                    # pred = model(x, xl)
                    loss = model.compute_loss(x, xl, tags)
                    gradients = tape.gradient(loss, model.trainable_variables)
                optimizer.apply_gradients(
                    zip(gradients, model.trainable_variables))
                loss = loss.numpy().sum()

                pbar.set_description(f'epoch: {i_epoch} loss: {loss:.4f}')

        self.tokenizer = tokenizer
        self.label = label
        self.model = model

    def predict(self, X):
        """Predict label."""
        assert self.model is not None, 'Intent not fit'
        x = self.tokenizer.texts_to_sequences(X)
        x = tf.keras.preprocessing.sequence.pad_sequences(x, padding='post')
        xl = np.array([len(x) for x in X])
        x = tf.convert_to_tensor(x, dtype=tf.float32)
        xl = tf.convert_to_tensor(xl, dtype=tf.int32)
        x = self.model(x, xl)
        x = x.numpy()
        x = [
            self.label.inverse_transform(xx)[:len(X[i])].tolist()
            for i, xx in enumerate(x)
        ]
        return x

    def __getstate__(self):
        """Pickle compatible."""
        state = self.__dict__.copy()
        if self.model is not None:
            state['model_weights'] = state['model'].get_weights()
            del state['model']
        return state

    def __setstate__(self, state):
        """Pickle compatible."""
        if 'model_weights' in state:
            model_weights = state.get('model_weights')
            del state['model_weights']
            self.__dict__.update(state)
            self.model = self.build_model()
            self.model.set_weights(model_weights)
        else:
            self.__dict__.update(state)
