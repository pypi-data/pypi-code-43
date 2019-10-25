"""
# Preprocessing

Submodule containing all the preprocessing classes to prepare text for
embeddings learning.

## Quick overview

The preprocessing module preprocesses the text/set of text in the following way :


1. Detects and replaces numbers/float by a generic token 'FLOAT', 'INT'

2. Add spaces in between punctuation so that tokenisation avoids adding 'word.' to the vocabulary instead of 'word', '.'

3. Lowers words

4. Recursive word phrases detection : with a simple probabilistic rule, gathers the tokens 'new', york' to a single token 'new_york'.

5. Frequency Subsampling : discards unfrequent words with a probability depending on their frequency.

The module enables to save a vocabulary file and the modified files.

## Usage example

Creating and saving a loadable configuration:
```python
from embeddings.preprocessing.preprocessor import PreprocessorConfig, Preprocessor
config = PreprocessorConfig('/tmp/logdir')
config.set_config(writing_dir='/tmp/outputs')
config.save_config()
```

```python
prep = Preprocessor('/tmp/logdir')  # Loads the config object in /tmp/logdir if it exists
prep.fit('~/mydata/')  # Fits the unigram & bigrams occurences
prep.filter()  # Filters with all the config parameters
prep.transform('~/mydata')  # Transforms the texts with the filtered vocab.
```


## Computational specifications

This code is intended to be robust to very large corpus and is then multiprocessed. The module automatically retrieves the number of threads available on the computer and reads the texts to fit and transform them in parallel over all threads. The module will automatically use all threads, and for now there is no option to change that. Please fill a github issue if such an option is needed.

## Detailed background

There are two main parts in Mikolov and al.'s preprocessing : learning word phrases like 'New York City' and gather it as a single token 'New_York_City'; and subsampling words regarding their frequencies.


### 1 Learning phrases

Inspired from the following article:
Mikolov, T., Sutskever, I., Chen, K., Corrado, G. S., & Dean, J. (2013). Distributed Representations of Words and Phrases and their Compositionality.

> Use of a simple data-driven approach, where phrases are formed based on the unigram and bigram counts:
<p align="center"><img src="https://latex.codecogs.com/gif.latex?score(w_i,%20w_j)%20=%20&#x5C;frac{count(w_iw_j)%20-%20&#x5C;delta}{count(w_i)&#x5C;cdot%20count(w_j)}"/></p>

> The <img src="https://latex.codecogs.com/gif.latex?&#x5C;delta"/> is used as a discounting coefficient and prevents too many phrases consisting of very infrequent words to be formed. The bigrams with score above the chosen threshold are then used as phrases. Typically, we run 2-4 passes over the training data with decreasing threshold value, allowing longer phrases that consists of several words to be formed. We evaluate the quality of the phrase representations using a new analogical reasoning task that involves phrases. Table 2 shows examples of the five categories of analogies used in this task. This dataset is publicly available on the [web](https://code.google.com/archive/p/word2vec/source/default/source )

Example, one pass:
```python
["New York City"] #sentence
[("New", "York"), ("York", "City")] # bigrams
["New_York", "City"] # new sentence if score > threshold
```

### 2. Frequency subsampling


In order to avoid too frequent words in the corpus, words are subsampled by computing their discarding probability:
<p align="center"><img src="https://latex.codecogs.com/gif.latex?&#x5C;mathbb{P}(&#x5C;text{Discarding%20}w_i)%20=%201-&#x5C;sqrt{&#x5C;frac{t}{f(w_i)}}"/></p>

Where <img src="https://latex.codecogs.com/gif.latex?f(w_i)"/> is the frequency of word <img src="https://latex.codecogs.com/gif.latex?i"/> over the whole corpus.
"""
