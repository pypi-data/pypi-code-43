"""# Embeddings


This package is designed to provide easy-to-use python class and cli
interfaces to:

- clean corpuses in an efficient way in terms of computation time

- generate word2vec embeddings (based on gensim) and directly write them to a format that is compatible with [Tensorflow Projector](http://projector.tensorflow.org/)

Thus, with two classes, or two commands, anyone should be able clean a corpus and generate embeddings that can be uploaded and visualized with Tensorflow Projector.

## Getting started

### Installation

To install this package, simply run :
```bash
pip install embeddingsprep
```

Further versions might include conda builds, but it's currently not the case.


### Requirements

This packages requires ```gensim```, ```nltk```, and ```docopt``` to run. If
pip doesn't install this dependencies automatically, you can install it by
running :
```bash
pip install nltk docopt gensim
```

## Main features

### Preprocessing

For Word2Vec, we want a soft yet important preprocessing. We want to denoise the text while keeping as much variety and information as possible. A detailed version of what is done during the preprocessing is available [here](./preprocessing/index.html)

**IMPORTANT WARNING** :
Your text data should be represented one of the two following ways :

- A simple .txt file, containing all your plain text data. This is not recommended as then, the preprocessing will not be multithreaded.

- A directory containing many .txt files. The Preprocessor will read all the files in the directory, and will be multithreaded.

#### Usage example :

First you need to create and save a Preprocessor configuration file:

```python
from embeddingsprep.preprocessing.preprocessor import PreprocessorConfig, Preprocessor
config = PreprocessorConfig('~/logdir')
config.set_config(writing_dir='~/outputs')  # You can additionnally change other preprocessing params.
config.save_config()
```

Here, ```'~/logdir'``` should be replaced by the path you want to log the preprocessing summary files in. The preprocessing summary files will contain, after fitting the preprocessor:

- ```vocabulary.json```, the saved final vocabulary, after word phrases gathering and frequency subsampling.

- ```WordPhrases.json```, the word phrases vocabulary.

- ```summary.txt```, a summary containing informations on the preprocessing fitting.

The ```writing_dir='~/outputs'``` argument indicates where the Preprocessor should write the processed files while transforming the data.


```python
prep = Preprocessor('/tmp/logdir')  # Loads the config object in /tmp/logdir if it exists
prep.fit('~/mydata/')  # Fits the unigram & bigrams occurences - must be done once
prep.filter()  # Filters with all the config parameters - can be done multiple times until the best parameters are found
prep.transform('~/mydata')  # Transforms the texts with the filtered vocab. 
```

You can additionnally redefine preprocessor parameters multiple times after fitting the data by accessing, for instance for the frequency threshold:
```python
prep.params['freq_threshold'] = 0.3
```


### Word2Vec

For the Word2Vec, we just wrote a simple wrapper that takes the
preprocessed files as an input, trains a Word2Vec model with gensim and writes the vocab, embeddings .tsv files that can be visualized with tensorflow projector (http://projector.tensorflow.org/)

#### Usage example:


```python
from embeddingsprep.models.word2vec import Word2Vec
model = Word2Vec(emb_size=300, window=5, epochs=3)
model.train('./my-preprocessed-data/')
model.save('./my-output-dir')
```

```'./my-preprocessed-data/'``` is the directory where the preprocessed files are stored. 

```'./my-output-dir'``` is the directory where the embeddings and model will be stored.

## Future work

Future work will include:

- Creation of a command line interface

- Embedding alignements methods

- More tutorials in the documentation

## Contributing

Any github issue, contribution or suggestion is welcomed! You can open issues on the [github repository](https://github.com/sally14/embeddings)."""
name = "embeddingsprep"
