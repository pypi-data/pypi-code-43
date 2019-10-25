"""
# Models

Submodules containing the models.


## Quick overview

For now, models only contains a simple wrapper for gensim's implementation of word2vec.

Its main advantage is to be directly compatible with our implementation of the preprocessing.

The Word2Vec model takes as an input :

- A bunch of preprocessed files, represented as a list of path, or the path of a directory containing plain, raw text files.

- The parameters of the model

The model has 3 main outputs :

- An ```embeddings.tsv``` file, containing one embedding per line, with each coordinates separated by a '\t' token. 

- ```A metadata.tsv``` file, containing 1 word per line, each line corresponding to the embedding on the same line in ```embeddings.tsv```. Warning : the first line of this file has a header, that the ```embeddings.tsv``` file doesn't have, resulting in a shift of one line in the ```embeddings.tsv``` - ```A metadata.tsv``` correspondence.

- A word2vec.model file with the trained gensim checkpoints to restore the model from. 

## Usage example

```python
from embeddingsprep.models.word2vec import Word2Vec
model = Word2Vec(emb_size=300, window=5, epochs=3)
model.train('./my-preprocessed-data/')
model.save('./my-output-dir')
```
"""
