"""
#                                Word2Vec

Wrapper for gensim's implementation.

Outputs embeddings to a tensorflow projector-readable format.

"""
import os
import gensim
import json
from glob import glob
from multiprocessing import cpu_count

from models.utils import read_files, open_vocab


class Word2Vec(object):
    """
    The class implementing a word2vec model.
    """

    def __init__(
        self,
        emb_size=200,
        window=10,
        epochs=10,
        min_count=1,
        restore_from=False,
    ):
        """Instantiate a word2vec model.
        Args:
            emb_size : int
                The size/dimension of the embedding to train. default : 200
            window : int
                The size of the window to train the embeddings on. default : 10
            epoch : int
                Number of epochs for training. default : 10
            min_count : int
                The minimum number of occurences a word must have to be
                included in the vocabulary. default : 1
            restore_from : bool or str
                False if the model is initialized from scratch. Path to a
                gensim word2vec model if the model is to be restored.
        """
        self.emb_size = emb_size
        self.window = window
        self.epochs = epochs
        self.min_count = min_count
        self.restore_from = restore_from

    def train(self, filenames):
        """ Trains the model with specified params.
        Args:
            filenames : str or list of str
                Path of file or directory to find the files to train the model on. Files should consist of plain, raw text, preprocessed with the Preprocessor.
        """
        if type(filenames) == list:
            filenames = filenames
        elif type(filenames) == str:
            if os.path.isdir(filenames):
                filenames = glob(os.path.join(filenames, "*"))
            elif os.path.isfile(filenames):
                filenames = [filenames]
            else:
                raise TypeError
        else:
            raise TypeError

        sents = read_files(filenames)
        if self.restore_from:
            assert os.path.isfile(
                self.restore_from
            ), "The path to restore model is not a file. Aborting"
            self.model = gensim.models.Word2Vec.load(self.restore_from)
        else:
            self.model = gensim.models.Word2Vec(
                sents,
                size=self.emb_size,
                window=self.window,
                min_count=self.min_count,
                workers=cpu_count(),
            )

        self.model.train(sents, total_examples=len(sents), epochs=self.epochs)

    def save(self, dir):
        """
        Saves the model in the given dir, all together with the correct embeddings.tsv, metadata.tsv files
        Args:
            dir : str
                the path to the saving directory
        """
        if not (os.path.isdir(dir)):
            os.mkdir(dir)
        self.model.save(os.path.join(dir, "word2vec.model"))
        try:
            vocab_path = glob(dir, "*.json")[0]
            vocab = open_vocab(vocab_path)
        except:
            vocab_keys = list(self.model.wv.vocab.keys())
            vocab = {vocab_keys[i]: i for i in range(len(vocab_keys))}

        inv_vocab = {v: k for k, v in vocab.items()}
        METADATA_PATH = os.path.join(dir, "metadata.tsv")
        VECTOR_PATHS = os.path.join(dir, "embeddings.tsv")
        with open(METADATA_PATH, "w", encoding="utf-8") as metadata:
            with open(VECTOR_PATHS, "w", encoding="utf-8") as vectors:
                metadata.write("WORD\tINDEX\n")
                for i in range(len(vocab)):
                    try:
                        vector = self.model.wv[inv_vocab[i]]
                        metadata.write(
                            str(inv_vocab[i]) + "\t" + str(i) + "\n"
                        )
                        n = len(vector)
                        for j in range(n):
                            if j == (n - 1):
                                vectors.write(str(vector[j]) + "\n")
                            else:
                                vectors.write(str(vector[j]) + "\t")
                    except:
                        print(
                            "{0} not in vocabulary. Passing. \n".format(
                                inv_vocab[i]
                            )
                        )
                        pass
