"""

#                        Multiprocessed Preprocessing


Classes for parallelized preprocessing of text. Contains two main classes :

- **PreprocessorConfig**, which is a tool to define, save, and read
preprocessing configurations : parameters, .
- **Preprocessor**, which is the tool to preprocess a large amount of file in
an optimized way.

The preprocessing is made of two main parts : first, the preprocessor has to
clean, and then learn all the unigram and bigram frequencies dictionnaries over
the corpus, to do word phrases detection and frequency subsampling.
Second, the preprocessor modifies the given files and writes it.

During each execution of the filter method, a summary is generated, giving some
statistics about the corpus.
"""
from preprocessing.utils.readers import (
    checkExistenceDir,
    checkExistenceFile,
    openFile,
)
from preprocessing.utils.readers import convertFloat, convertInt
from preprocessing.utils.structure import melt_vocab_dic
from preprocessing.utils.structure import get_unigram_voc, get_bigram_voc

import json
import gc
import os
import logging

from collections import OrderedDict
from random import seed
from random import uniform
from numpy import sqrt
from nltk.tokenize import ToktokTokenizer
from multiprocessing import Pool
from multiprocessing import cpu_count
from glob import glob
from hashlib import sha1


logger = logging.getLogger("preprocessor")


class PreprocessorConfig(object):
    """PreprocessorConfig is a util to write, load, and
    save preprocessors parameter configurations
    """

    def __init__(self, log_dir):
        checkExistenceDir(log_dir)
        self.log_dir = log_dir
        self.has_config = False

    def set_config(
        self,
        n_iter_phrases=1,
        phrases_delta=0,
        phrases_threshold=1e-1,
        freq_threshold=0.1,
        writing_dir="",
        vocabulary_size=None,
    ):
        """Instantiate a new preprocessor configuration

        Args:
            n_iter_phrases : float
                number of iteration for word phrases detection, default : 1
            phrases_delta : float
                delta parameter in word phrase detection, default : 0
            phrases_threshold : float
                threshold parameter in word phrase detection, default : 1e-3
            freq_threshold : float
                frequency subsampling threshold, default : 1e-5
            writing_dir : str
                path where preprocessed files are going to be written
            vocabulary_size : int
                maximum size of the vocabulary
        """
        self.params = {}
        self.params["n_iter_phrases"] = n_iter_phrases
        self.params["phrases_delta"] = phrases_delta
        self.params["phrases_threshold"] = phrases_threshold
        self.params["freq_threshold"] = freq_threshold
        checkExistenceDir(writing_dir)
        self.params["writing_dir"] = writing_dir
        self.params["vocabulary_size"] = vocabulary_size
        self.has_config = True

    def save_config(self):
        """Saves the configuration class as a parameter json in the log_dir
        dir"""
        if self.has_config:
            with open(
                os.path.join(self.log_dir, "PreprocessorConfig.json"), "w"
            ) as f:
                json.dump(self.params, f)
        else:
            logger.error("PreprocessorConfig has not been configurated")

    def read_config(self):
        """Reads an existing config, that must be in the log_dir directory"""
        with open(
            os.path.join(self.log_dir, "PreprocessorConfig.json"), "r"
        ) as f:
            self.params = json.load(f)
        self.has_config = True


class Preprocessor(PreprocessorConfig):
    """A Preprocessor object inherits from a PreprocessorConfig object to
    initialize its parameters. Then, it does 5 things :

    1. Detects and replaces numbers/float by a generic token 'FLOAT', 'INT'
    2. Add spaces in between punctuation so that tokenisation avoids adding
    'word.' to the vocabulary instead of 'word', '.'.
    3. Lowers words
    4. Recursive word phrases detection : with a simple probabilistic rule,
    gathers the tokens 'new', york' to a single token 'new_york'.
    5. Frequency Subsampling : discards unfrequent words with a probability
    depending on their frequency.

    It works with 2 main methods, '.fit' and .'transform'. The first method
    fits the vocabulary (which implies to lower, tokenize, do the word
    phrase detection and frequency subsampling). Fitting the vocabulary implies
    to calculate word frequencies over all the corpus, which can be a challenge
    when parallelizing the code.
    The 'transform' method then uses the learned vocabulary to re-write clean
    files in the 'writing_dir' directory. This method is also parallelized over
    all the cpus available.

    Usage example:
    ```python
    prep = Preprocessor('/tmp/logdir')  # We suppose we already have a
    # PreprocessorConfig saved in /tmp/logdir
    prep.fit('~/mydata/')
    prep.filter()
    prep.transform('~/mydata')
    ```
    """

    def __init__(self, log_dir, from_log=False):
        self.log_dir = log_dir
        if checkExistenceFile(
            os.path.join(log_dir, "PreprocessorConfig.json")
        ):
            self.read_config()
        self.tok = ToktokTokenizer()
        self.parsing_char_ = sha1(b"sally14").hexdigest()
        self.fitted = False
        if from_log:
            self.fitted = True
            with open(
                os.path.join(self.log_dir, "vocabulary.json"),
                "r",
                encoding="utf-8",
            ) as f:
                self.vocabulary_ = json.load(f)
            with open(
                os.path.join(self.log_dir, "WordPhrases.json"),
                "r",
                encoding="utf-8",
            ) as f:
                p = json.load(f)
                self.phrasewords_ = {
                    i.replace("_", self.parsing_char_): p[i] for i in p.keys()
                }

    def get_batches(self, filenames):
        """Defines the filename batches to multiprocess fitting and transformation
        Args:
            filenames : str or list of str
                a list of files or a directory containing the files to fit/
                transform the data on.
        Returns:
            batches : list of list of str
                the list of batches (lists of filenames)
        """
        if type(filenames) == str:
            if os.path.isdir(filenames):
                ls = glob(os.path.join(filenames, "*"))
        elif type(filenames) == list:
            ls = filenames
        else:
            logger.error("Bad type for filenames, must be str or list of str")
        batches = []
        cpu = cpu_count()
        n = len(ls)
        if n >= cpu:
            for i in range(cpu - 1):
                batches.append(ls[(n // cpu) * i : (n // cpu) * (i + 1)])
            batches.append(ls[(n // cpu) * (cpu - 1) :])
        else:
            batches = list(map(lambda x: [x], ls))
        assert len(batches) == min(cpu, n)
        return batches

    def fit_batch(self, filebatch):
        """
        Fits one batch
        Args:
            filebatch : list of str
                the list of file names in the given batch
        Returns:
            unig : dic
                fitted unigram dictionnary
            big : dic
                fitted bigram dictionnary
        """
        unig = {}
        big = {}
        for file in filebatch:
            text = openFile(file)
            cleaned_text = self.clean(text)
            unig = melt_vocab_dic(get_unigram_voc(cleaned_text), unig)
            big = melt_vocab_dic(
                get_bigram_voc(cleaned_text, self.parsing_char_), big
            )
            del text
            del cleaned_text
        return [unig, big]

    def fit(self, filenames):
        """
        Parallelizes the fitting & definition of vocabulary, dumped in
        self.log_dir
        Args:
            filenames : str or list of str
                the list of file names in the given batch
        """
        logger.info("Started fitting")
        batches = self.get_batches(filenames)
        logger.info(
            "Defined {} batches for multiprocessing".format(cpu_count())
        )
        logger.info("Starting parallelized fitting")
        pool = Pool(processes=cpu_count())
        results = pool.map(self.fit_batch, batches)
        pool.close()
        pool.terminate()
        pool.join()
        logger.info("Received {} batches results")
        logger.info("Melting unigram and bigrams dictionnaries")
        self.unigram_dic_ = {}
        self.bigram_dic_ = {}
        for j in range(len(results)):
            self.unigram_dic_ = melt_vocab_dic(
                self.unigram_dic_, results[j][0]
            )
            self.bigram_dic_ = melt_vocab_dic(self.bigram_dic_, results[j][1])
            results[j] = 0  # Clears memory
        del results
        gc.collect()
        with open(
            os.path.join(self.log_dir, "unigrams.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(self.unigram_dic_, f)
        with open(
            os.path.join(self.log_dir, "bigrams.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(self.bigram_dic_, f)

    def filter(self):
        """Filters the results based on the configuration, saves the
        vocabulary and the word phrases"""
        logger.info("Building word phrases score")
        with open(
            os.path.join(self.log_dir, "unigrams.json"), "r", encoding="utf-8"
        ) as f:
            self.unigram_dic_ = json.load(f)
        with open(
            os.path.join(self.log_dir, "bigrams.json"), "r", encoding="utf-8"
        ) as f:
            self.bigram_dic_ = json.load(f)
        self.build_score()
        self.phrasewords_ = {}
        self.phrasewords()
        self.vocabulary_ = {}
        self.build_vocab()
        self.wordcount2freq()
        logger.info("Subsampling unfrequent words")
        self.subsample_freq_dic()
        logger.info("Corpus fitted")
        self.fitted = True
        logger.info("Saving vocabulary")
        with open(
            os.path.join(self.log_dir, "vocabulary.json"),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(self.vocabulary_, f)
        self.save_word_phrases()
        self.get_summary()

    def clean(self, text):
        """Parses a text, tokenize, lowers and replace ints and floats by a
        special token
        Args:
            text : str
                a text represented as a string
        Returns:
            words : str
                a clean text
        """
        words = self.tok.tokenize(text)
        words = " ".join(
            map(lambda x: convertFloat(convertInt(x.lower())), words)
        )
        return words

    def build_score(self):
        """
        Add bigram score to the 'bigram_dic_' dictionnary.
        bigram_dic_ = {bigram : occurences} becomes:
        bigram_dic_ = {bigram : (occurences, score)}
        """
        for bigrams in self.bigram_dic_.keys():
            i, j = bigrams.split(self.parsing_char_)
            score = (
                self.bigram_dic_[bigrams] - self.params["phrases_delta"]
            ) / (self.unigram_dic_[i] * self.unigram_dic_[j])
            self.bigram_dic_[bigrams] = (self.bigram_dic_[bigrams], score)

    def build_vocab(self):
        """
        Create a dictionnary 'vocabulary_' which contains unigrams and word
        phrases, with their occurences.
        """
        copy_dict = self.unigram_dic_.copy()
        for word in self.bigram_dic_:
            # First feed the vocabulary with bigrams :
            if word in self.phrasewords_:
                try:
                    i, j = (word.replace(self.parsing_char_, " ", 1)).split()
                    # delete unigrams if unigrams only appear in a given bigram
                    if self.unigram_dic_[i] == self.phrasewords_[word]:
                        try:
                            # Delete element from copy_dict and not
                            # unigram_dic_
                            del copy_dict[i]
                        except:
                            pass
                    if self.unigram_dic_[j] == self.phrasewords_[word]:
                        try:
                            del copy_dict[j]
                        except:
                            pass
                    self.vocabulary_[
                        word.replace(self.parsing_char_, "_")
                    ] = self.phrasewords_[word]
                except:
                    pass
        self.vocabulary_ = melt_vocab_dic(copy_dict, self.vocabulary_)

    def phrasewords(self):
        """
        Create a dictionnary 'phrasewords_' which contains word
        phrases, with their occurences.
        """
        for bigrams in self.bigram_dic_:
            if self.bigram_dic_[bigrams][1] > self.params["phrases_threshold"]:
                self.phrasewords_[bigrams] = self.bigram_dic_[bigrams][0]

    def wordcount2freq(self):
        """
        Create the 'vocab_freq_' dictionnary : goes from a vocabulary_
        dictionnary with occurences to a dictionnary of the vocabulary with
        frequencies. Useful for frenquency subsampling.
        """
        count = 0
        dico = self.vocabulary_
        dico2 = {}
        for i in dico:
            count = count + dico[i]
        for i in dico:
            newkey = i.replace(self.parsing_char_, "_", 1)
            dico2[newkey] = dico[i] / count
        self.vocab_freq_ = dico2

    def subsample_freq_dic(self):
        """
        Vocab dictionnary frequency subsampling.
        $$p = 1 - \sqrt{\frac{t}{f}}$$
        With $f$ the frequency of a given word, and $p$ probability
        to discard the word.
        """
        t = self.params["freq_threshold"]
        vocab = self.vocab_freq_
        for word in self.vocab_freq_.keys():
            try:  # In some very rare cases, doesn't work
                # Computing discarding word probability (Mik. 2013)
                freq = vocab[word]
                prob = 1 - sqrt(t / freq)
                # Simulating a uniform [0,1]
                # First initiate a random seed
                seed("sally14")  # random.seed() function hashes strings
                # Simulate a binomial B(prob)
                x = uniform(0, 1)
                if x < prob:
                    del self.vocabulary_[word]
            except:
                pass
        # Order vocab by frequency:
        self.vocabulary_ = OrderedDict(
            sorted(self.vocabulary_.items(), key=lambda x: x[1], reverse=True)
        )
        # Cuts if max_voc_size
        if self.params["vocabulary_size"] is not None:
            self.vocabulary_ = {
                k: self.vocabulary_[k]
                for k in self.vocabulary_.keys()[
                    : self.params["vocabulary_size"]
                ]
            }

    def wordphrases(self, t):
        """
        word phrases gathering (in a single token, gathered with _ ).
        Args:
            t : str
                a text to clean
        Returns:
            t : str
                the cleaned text
        """
        count = 0
        words = t.split(" ")
        new_words = []
        # First handling the case where the text is just one word :
        # cannot generate any bigram.
        if len(words) == 1:
            new_words = words
        # Then regular cases :
        else:
            j = 0
            while j < (len(words) - 1):  # = for each word in the sentence
                big = (
                    words[j],
                    words[j + 1],
                )  # getting the (j-th, j+1-th)words
                # writing the corresponding bigram :
                bigrams = self.parsing_char_.join(big)
                # If the bigram is enough frequent to be gathered :
                if bigrams in self.phrasewords_:
                    # Then add the bigram as a new word in 'new_sent_sent'
                    new_words.append("_".join(big))
                    count = count + 1  # Count the number of gathered
                    # bigrams
                    # Directly go to the j+2-th word in order to avoid
                    # repeating the j+1-th word
                    j = j + 2
                # If the bigram is not frequent enough :
                else:
                    if j == (len(words) - 2):
                        new_words.append(words[j])
                        new_words.append(words[j + 1])
                        j = j + 2
                    # Add j-th word
                    else:
                        new_words.append(words[j])
                        # Go to j+1-th word
                        j = j + 1

        return " ".join(new_words)

    def transform_batch(self, filebatch):
        """ Transforms a batch by cleaning the text, gathering word phrases,
        replacing subsampled words by UNK token.
        Args:
            filebatch : list of str
                the list of paths to the files
        """
        for file in filebatch:
            new_file = os.path.join(
                self.params["writing_dir"],
                os.path.basename(file) + "_cleaned" + ".txt",
            )

            text = openFile(file)
            cleaned_text = self.clean(text)
            del text
            # Words phrases gathering
            cleaned_text = self.wordphrases(cleaned_text)
            # Frequency subsampling
            cleaned_text = " ".join(
                map(
                    lambda x: "UNK"
                    if (x not in self.vocabulary_.keys())
                    else x,
                    cleaned_text.split(" "),
                )
            )
            with open(new_file, "w", encoding="utf-8") as f:
                f.write(cleaned_text)
            gc.collect()

    def transform(self, filenames):
        """
        Parallelizes the transformation, dumped in writing_dir
        Args:
            filenames : str or list of str
                the list of file names in the given batch
        """
        if not self.fitted:
            logger.error("No fitting, aborting")
        else:
            logger.info("Started transform")
            batches = self.get_batches(filenames)
            logger.info(
                "Defined {} batches for multiprocessing".format(cpu_count())
            )
            logger.info("Starting parallelized transforming")
            pool = Pool(processes=cpu_count())
            pool.map(self.transform_batch, batches)
            pool.close()
            pool.terminate()
            pool.join()
            logger.info("Succesfully transformed all the files")

    def save_word_phrases(self):
        """Saves word phrases as a json file in log_dir
        """
        cleaned_phrases = {
            k.replace(self.parsing_char_, "_"): self.phrasewords_[k]
            for k in self.phrasewords_.keys()
        }
        with open(
            os.path.join(self.log_dir, "WordPhrases.json"),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(cleaned_phrases, f)

    def get_summary(self):
        """ Writes a summary of the fitting in the log_dir
        """
        with open(
            os.path.join(self.log_dir, "summary.txt"), "w", encoding="utf-8"
        ) as text:
            text.write("Attributes: \n-------------------- \n")
            text.write(
                "len(unigram_dic_) : "
                + str(len(self.unigram_dic_))
                + "\n"
                + "len(bigram_dic_) : "
                + str(len(self.bigram_dic_))
                + "\n"
                + "len(phrasewords_) : "
                + str(len(self.phrasewords_))
                + "\n"
                + "len(vocabulary_) : "
                + str(len(self.vocabulary_))
                + "\n \n"
            )
            text.write("Bigram Dic extract :\n-------------------\n")
            dico = self.bigram_dic_
            head = dict(
                [
                    (key.replace(self.parsing_char_, "_"), dico[key])
                    for key in sorted(dico.keys())[
                        len(dico) // 2 : len(dico) // 2 + 20
                    ]
                ]
            )
            text.write(str(head))
            text.write("\n\nPhrasewords Dic extract :\n-------------------\n ")
            dico = self.phrasewords_
            head = dict(
                [
                    (key.replace(self.parsing_char_, "_"), dico[key])
                    for key in sorted(dico.keys())[
                        len(dico) // 2 : len(dico) // 2 + 20
                    ]
                ]
            )
            text.write(str(head))
