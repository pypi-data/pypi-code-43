import pytest

import JLpyUtils.ML as ML

text_list = ['Marietta Boulevard Northwest', 'Peachtree Street Southwest', 'Mitchell Street Southwest']

def test_word2vect():
    
    Vectorizer = ML.NeuralNet.Bert.Word2Vec(model_ID = 'bert-base-uncased')
    vectors = [Vectorizer.fit_transform(text) for text in text_list]
    
    assert(len(vectors[0])==768)