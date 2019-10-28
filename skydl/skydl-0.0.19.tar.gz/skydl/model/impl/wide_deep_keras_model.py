# -*- coding: utf-8 -*-
from skydl.model.default_keras_model import DefaultKerasModel
from skydl.model.train_phase_enum import TrainPhaseEnum
import pandas as pd
import numpy as np
import sys,os
sys.path.append(os.path.abspath('%s/..' % sys.path[0]))


class WideDeepKerasModel(DefaultKerasModel):
    """
    wide&deep model, paper: https://arxiv.org/pdf/1606.07792.pdf
    """
    def adjust_parse_args_value(self):
        super().adjust_parse_args_value()
        self.parser_args.data_path = sys.path[0] + '/../../dataset'
        self.parser_args.use_cuda = True
        self.parser_args.init_from_saver = True
        self.parser_args.train_phase = TrainPhaseEnum.Train.value
        self.parser_args.model_version = '1'
        self.parser_args.epochs = 10
        self.parser_args.batch_size = 128
        self.parser_args.log_interval = 1000

    def load_data(self):
        super().load_data()
        # Get the data: original source is here: https://www.kaggle.com/zynicide/wine-reviews/data
        # URL = "https://storage.googleapis.com/sara-cloud-ml/wine_data.csv"
        # path = tf.keras.utils.get_file(URL.split('/')[-1], URL)
        wine_data = pd.read_csv(self.parser_args.data_path + "/wine_data/wine_data.csv")
        # Shuffle the data
        wine_data = wine_data.sample(frac=1)
        # Print the first 5 rows
        print(wine_data.head())
        # Do some preprocessing to limit the # of wine varities in the dataset
        wine_data = wine_data[pd.notnull(wine_data['country'])]
        wine_data = wine_data[pd.notnull(wine_data['price'])]
        wine_data = wine_data.drop(wine_data.columns[0], axis=1)
        variety_threshold = 500  # Anything that occurs less than this will be removed.
        value_counts = wine_data['variety'].value_counts()
        to_remove = value_counts[value_counts <= variety_threshold].index
        wine_data.replace(to_remove, np.nan, inplace=True)
        wine_data = wine_data[pd.notnull(wine_data['variety'])]
        # Split data into train and test
        train_size = int(len(wine_data) * 0.8)
        print("Train size: %d" % train_size)
        print("Test size: %d" % (len(wine_data) - train_size))
        # Train features
        description_train = wine_data['description'][:train_size]
        variety_train = wine_data['variety'][:train_size]
        # Train labels
        labels_train = wine_data['price'][:train_size]
        # Test features
        description_test = wine_data['description'][train_size:]
        variety_test = wine_data['variety'][train_size:]
        # Test labels
        labels_test = wine_data['price'][train_size:]
        return description_train, variety_train, labels_train, description_test, variety_test, labels_test

    def fit(self):
        if not self.is_training_phase():
            return self
        from sklearn.preprocessing import LabelEncoder
        from tensorflow.python import keras
        description_train, \
        variety_train, \
        labels_train, \
        description_test, \
        variety_test, \
        labels_test = self.load_data()
        # Create a tokenizer to preprocess our text descriptions
        vocab_size = 12000  # This is a hyperparameter, experiment with different values for your dataset
        tokenize = keras.preprocessing.text.Tokenizer(num_words=vocab_size, char_level=False)
        tokenize.fit_on_texts(description_train)  # only fit on train
        # vocab_size = len(tokenize.word_counts.keys())
        # print(vocab_size)
        # Wide feature 1: sparse bag of words (bow) vocab_size vector
        description_bow_train = tokenize.texts_to_matrix(description_train)
        description_bow_test = tokenize.texts_to_matrix(description_test)
        # Wide feature 2: one-hot vector of variety categories
        # Use sklearn utility to convert label strings to numbered index
        encoder = LabelEncoder()
        encoder.fit(variety_train)
        variety_train = encoder.transform(variety_train)
        variety_test = encoder.transform(variety_test)
        num_classes = np.max(variety_train) + 1
        # Convert labels to one hot
        variety_train = keras.utils.to_categorical(variety_train, num_classes)
        variety_test = keras.utils.to_categorical(variety_test, num_classes)
        # Define our wide model with the functional API
        bow_inputs = keras.layers.Input(shape=(vocab_size,))
        variety_inputs = keras.layers.Input(shape=(num_classes,))
        merged_layer = keras.layers.concatenate([bow_inputs, variety_inputs])
        merged_layer = keras.layers.Dense(256, activation='relu')(merged_layer)
        predictions = keras.layers.Dense(1)(merged_layer)
        wide_model = keras.Model(inputs=[bow_inputs, variety_inputs], outputs=predictions)
        wide_model.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
        print(wide_model.summary())
        # Deep model feature: word embeddings of wine descriptions
        train_embed = tokenize.texts_to_sequences(description_train)
        test_embed = tokenize.texts_to_sequences(description_test)
        max_seq_length = 170
        train_embed = keras.preprocessing.sequence.pad_sequences(train_embed, maxlen=max_seq_length, padding="post")
        test_embed = keras.preprocessing.sequence.pad_sequences(test_embed, maxlen=max_seq_length, padding="post")
        # Define our deep model with the Functional API
        deep_inputs = keras.layers.Input(shape=(max_seq_length,))
        embedding = keras.layers.Embedding(vocab_size, 8, input_length=max_seq_length)(deep_inputs)
        embedding = keras.layers.Flatten()(embedding)
        embed_out = keras.layers.Dense(1)(embedding)
        deep_model = keras.Model(inputs=deep_inputs, outputs=embed_out)
        print(deep_model.summary())
        deep_model.compile(loss='mse',
                           optimizer='adam',
                           metrics=['accuracy'])
        # Combine wide and deep into one model
        merged_out = keras.layers.concatenate([wide_model.output, deep_model.output])
        merged_out = keras.layers.Dense(1)(merged_out)
        combined_model = keras.Model(wide_model.input + [deep_model.input], merged_out)
        print(combined_model.summary())
        combined_model.compile(loss='mse',
                               optimizer='adam',
                               metrics=['accuracy'])
        # Run training
        combined_model.fit([description_bow_train, variety_train] + [train_embed], labels_train, epochs=self.parser_args.epochs, batch_size=self.parser_args.batch_size)
        combined_model.evaluate([description_bow_test, variety_test] + [test_embed], labels_test, batch_size=self.parser_args.batch_size)
        # Generate predictions
        predictions = combined_model.predict([description_bow_test, variety_test] + [test_embed])
        # Compare predictions with actual values for the first few items in our test dataset
        num_predictions = 40
        diff = 0
        for i in range(num_predictions):
            val = predictions[i]
            print(description_test.iloc[i])
            print('Predicted: ', val[0], 'Actual: ', labels_test.iloc[i], '\n')
            diff += abs(val[0] - labels_test.iloc[i])
        # Compare the average difference between actual price and the model's predicted price
        print('Average prediction difference: ', diff / num_predictions)
        return self

    def evaluate(self, *args, **kwargs):
        return self

    def serving(self):
        return self

