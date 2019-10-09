
from __future__ import print_function, division, absolute_import
from keras.models import Model
from keras.layers import Embedding, Dense, Dropout, Input, Reshape, Concatenate
from keras.optimizers import Adam
import logging
import numpy as np
from sklearn import base
from kaggler.preprocessing import LabelEncoder


MIN_EMBEDDING = 4
logger = logging.getLogger('Kaggler')


class EmbeddingEncoder(base.BaseEstimator):
    """EmbeddingEncoder encodes categorical features to numerical embedding features."""

    def __init__(self, cat_cols, num_cols=[], n_emb=[], min_obs=10, random_state=42):
        """Initialize an EmbeddingEncoder class object.

        Args:
            cat_cols (list of str): the names of categorical features to create embeddings for.
            num_cols (list of str): the names of numerical features to train embeddings with.
            n_emb (int or list of int): the numbers of embedding features used for columns.
            min_obs (int): categories observed less than it will be grouped together before training embeddings
            random_state (int): random seed.
        """
        self.cat_cols = cat_cols
        self.num_cols = num_cols

        if isinstance(n_emb, int):
            self.n_emb = [n_emb] * len(cat_cols)
        elif isinstance(n_emb, list):
            if n_emb:
                self.n_emb = [None] * len(cat_cols)
            else:
                assert len(cat_cols) == len(n_emb)
                self.n_emb = n_emb
        else:
            raise ValueError('n_emb should be int or list')

        self.random_state = random_state
        self.lbe = LabelEncoder(min_obs=self.min_obs)

    def fit(self, X, y):
        """Train a neural network model with embedding layers.

        Args:
            X (pandas.DataFrame): categorical features to create embeddings for
            y (pandas.Series): a target variable

        Returns:
            A trained EmbeddingEncoder object.
        """
        X_cat = self.lbe.fit_transform(X[self.cat_cols])

        inputs = []
        num_inputs = []
        embeddings = []
        self.embedding_layer_names = []
        features = []
        for i, col in enumerate(self.cat_cols):
            features.append(X_cat[col].values)

            if not self.n_emb[i]:
                n_uniq = X_cat[col].nunique()
                self.n_emb[i] = max(MIN_EMBEDDING, 2 * int(np.log2(n_uniq)))

            _input = Input(shape=(1,), name=col)
            _embed = Embedding(input_dim=n_uniq, output_dim=self.n_emb[i], name=col)(_input)
            _embed = Dropout(.2)(_embed)
            _embed = Reshape((self.n_emb[i],))(_embed)

            inputs.append(_input)
            embeddings.append(_embed)

        if self.num_cols:
            num_inputs = Input(shape=(len(self.num_cols),), name='num_inputs')
            merged_input = Concatenate(axis=1)(embeddings + [num_inputs])

            inputs = inputs + [num_inputs]
            features = features + [X[self.num_cols].values]
        else:
            merged_input = Concatenate(axis=1)(embeddings)

        x = Dense(128, activation='relu')(merged_input)
        x = Dropout(.5)(x)
        x = Dense(64, activation='relu')(x)
        x = Dropout(.5)(x)
        output = Dense(1, activation='linear')(x)

        self.model = Model(inputs=inputs, outputs=output)
        self.model.compile(optimizer=Adam(lr=0.01),
                           loss='mse',
                           metrics=['mse'])

        self.model.fit(x=features,
                       y=y,
                       epochs=100,
                       validation_split=.2,
                       batch_size=128)

        self.embs = []
        for i, col in enumerate(self.cat_cols):
            self.embs.append(self.model.get_layer(col).get_weights()[0])
            logger.debug('{}: {}'.format(col, self.embs[i].shape))

    def transform(self, X):
        X_cat = self.lbe.transform(X[self.cat_cols])
        X_emb = []
        for i, col in enumerate(self.cat_cols):
            X_emb.append(self.embs[X_cat[col].values])

        return np.hstack(X_emb)

    def fit_transform(self, X, y):
        self.fit(X, y)
        return self.transform(X)
