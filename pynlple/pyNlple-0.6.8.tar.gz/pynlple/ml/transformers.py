"""
    This module implements custom transformations of Sklearn's Pipeline
"""
from pynlple.processing.text import WSTokenizer as StringWSTokenizer
from pynlple.processing.text import RuleTokenizer as StringRuleTokenizer

from pandas import DataFrame, Categorical
from pandas.api.types import CategoricalDtype
import numpy as np
from sklearn.preprocessing._function_transformer import _identity
from sklearn.feature_extraction import DictVectorizer
from sklearn.base import BaseEstimator, TransformerMixin, ClassifierMixin


class NgramGenerator(object):

    def __init__(self, ngram_size=(1,1), join_s=' '):
        self.__size = ngram_size
        if self.__size[0] > self.__size[1]:
            raise ValueError('')
        self.__joiner = join_s
        super().__init__()

    def __call__(self, seq):
        # handle token n-grams
        min_n, max_n = self.__size
        if max_n != 1:
            original_seq = seq
            seq = []
            n_original_tokens = len(original_seq)
            for n in range(min_n,
                            min(max_n + 1, n_original_tokens + 1)):
                for i in range(n_original_tokens - n + 1):
                    seq.append(self.__joiner.join(original_seq[i: i + n]))
        return seq


class SENgramGenerator(object):

    def __init__(self, ngram_size=(1,1), join_s=' ', s=None, e=None):
        self.__size = ngram_size
        if len(self.__size) <= 0 or len(self.__size) > 2:
            raise ValueError('Ngram_size cannot be of length {}. Please pass a tuple(min,max)'.format(str(len(self.__size))))
        self.__min_n, self.__max_n = self.__size
        if self.__size[0] > self.__size[1]:
            raise ValueError('Max ngram_size cannot be bigger than min ngram size.')
        if self.__min_n < 1:
            raise ValueError('Min ngram_size cannot be smaller than 1.')
        if self.__min_n < 1:
            raise ValueError('Max ngram_size cannot be smaller than 1.')
        self.__s = s
        self.__e = e
        self.__joiner = join_s

        if self.__max_n > 1:
            self._ngrams = self._manygramm
        else:
            self._ngrams = self._onegramm

        if self.__s is not None and self.__e is None:
            self._preprocess = self._start
        elif self.__e is not None and self.__s is None:
            self._preprocess = self._end
        elif self.__s is not None and self.__e is not None:
            self._preprocess = self._start_end
        else:
            self._preprocess = self._pass
        super().__init__()

    def __call__(self, seq):
        return self._ngrams(list(self._preprocess(seq)))

    def _onegramm(self, seq):
        return seq

    def _manygramm(self, seq):
        gramms = []
        seq_len = len(seq)
        for n in range(self.__min_n, min(self.__max_n + 1, seq_len + 1)):
            for i in range(seq_len - n + 1):
                gramms.append(self.__joiner.join(seq[i: i + n]))
        return gramms

    def _start(self, seq):
        yield self.__s
        yield from seq

    def _end(self, seq):
        yield from seq
        yield self.__e

    def _start_end(self, seq):
        yield self.__s
        yield from seq
        yield self.__e

    def _pass(self, seq):
        yield from seq


class ColumnEqualFeature(BaseEstimator, TransformerMixin):

    def __init__(self, col_selector, opp_col_selector):
        self.col_selector = col_selector
        self.opp_col_selector = opp_col_selector

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return self.col_selector.transform(X) == self.opp_col_selector.transform(X)

    def get_params(self, deep=True):
        return {'col_selector': self.col_selector, 'opp_col_selector': self.opp_col_selector}


class VocabularyFeature(BaseEstimator, TransformerMixin):

    def __init__(self, entity_tagger, overlap_entities=False):
        self.__tagger = entity_tagger
        self.__overlap = overlap_entities

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.apply(lambda x: [e[2] for e in self.__tagger.get_tagged_entities(x, self.__overlap)])


class SubCategoryGenerator(BaseEstimator, TransformerMixin):

    def __init__(self, ngram_size=(1,1), join_s='/'):
        self.__ngram_size = ngram_size
        self.__join_s = join_s
        self.__ngrams = NgramGenerator(ngram_size=self.__ngram_size, join_s=self.__join_s)

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.apply(lambda x: [self.__ngrams(e.split(self.__join_s)) for e in x])


class ThresholdRuleVectorClassifier(BaseEstimator, ClassifierMixin):

    def __init__(self, default_class=0):
        self.default_class = default_class

    def fit(self, X, y):
        self.rules_ = X
        self.classes_ = y
        return self

    def transform(self, X):
        return X

    def __compare_each_row(self, row):
        answers = np.zeros((self.rules_.shape[0]), dtype=self.classes_.dtype)
        for i in np.arange(self.rules_.shape[0]):
            if np.all(row >= self.rules_[i]):
                answers[i] = self.classes_[i]
            else:
                answers[i] = self.default_class
        return answers

    def predict(self, X):
        return np.apply_along_axis(
            self.__compare_each_row,
            axis=1,
            arr=X
        )


class NumFeatureThresholdProbabilityPredictor(BaseEstimator, ClassifierMixin):

    def __init__(self, value_threshold=5, class_thres=0.5):
        self._min_value = value_threshold
        self._thres = class_thres
        self._step = self._thres / self._min_value
        super().__init__()

    def fit(self, X, y):
        self.classes_ = np.unique(y)
        return self

    def predict_proba(self, X):
        negative_probas = (X - self._min_value) * self._step
        conditional_negative_probas = np.where(X < self._min_value, -negative_probas, 0.0)
        res = np.vstack(((self._thres + conditional_negative_probas).T, (self._thres - conditional_negative_probas).T))
        return res.T

    def predict(self, X):
        return np.where(self.predict_proba(X)[:,0] < self._thres, *self.classes_.tolist())

    def get_params(self, deep=False):
        return {'class_thres': self._thres,
                'value_threshold': self._min_value}


class ThresholdClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, threshold=0.5):
        """Classify samples based on whether they are above of below `threshold`"""
        self.threshold = threshold

    def fit(self, X, y):
        self.classes_ = np.unique(y)
        return self

    def predict(self, X):
        # the implementation used here breaks ties differently
        # from the one used in RFs:
        #return self.classes_.take(np.argmax(X, axis=1), axis=0)
        return np.where(X[:, 0] > self.threshold, *self.classes_.tolist())

    def get_params(self, deep=False):
        return {'threshold': self.threshold}


class ItemSelector(BaseEstimator, TransformerMixin):

    def __init__(self, field_name):
        self.field = field_name

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X[self.field]

    def get_params(self, deep=False):
        return {'field_name': self.field}


class PandasSelector(BaseEstimator, TransformerMixin):

    def __init__(self, col_indexer=None, row_indexer=None):
        self.col_indexer = col_indexer
        self.row_indexer = row_indexer

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        if self.col_indexer and self.row_indexer:
            return X.loc[self.row_indexer, self.col_indexer]
        elif self.col_indexer and not self.row_indexer:
            return X.loc[:,self.col_indexer]
        elif not self.col_indexer and self.row_indexer:
            return X.loc[self.row_indexer]
        else:
            return X

    def get_params(self, deep=False):
        return {'col_indexer': self.col_indexer,
                'row_indexer': self.row_indexer}


class SelectorFunctionTransformer(BaseEstimator, TransformerMixin):

    def __init__(self, selectors, func=None, inverse_func=None,
                 kw_args=None, inv_kw_args=None):
        self.selectors = selectors
        self.func = func
        self.inverse_func = inverse_func
        self.kw_args = kw_args
        self.inv_kw_args = inv_kw_args

    def fit(self, X, y=None):
        self.selectors = [v.fit(X, y) for v in self.selectors]
        return self

    def transform(self, X, y=None):
        return self._transform(selected_features=[v.transform(X,y) for v in self.selectors],
                               kw_args=self.kw_args, func=self.func)

    def inverse_transform(self, X, y=None):
        return self._transform(selected_features=[v.inverse_transform(X,y) for v in self.selectors],
                               kw_args=self.inv_kw_args, func=self.func)

    def _transform(self, selected_features, kw_args=None, func=None):
        if func is None:
            func = _identity
        return func(*selected_features, **kw_args if kw_args else {})


class ApplyToSeries(BaseEstimator, TransformerMixin):

    def __init__(self, func, *args, **kwds):
        self.func = func
        self.args = args
        self.kwds = kwds
        super().__init__()

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X.apply(func=self.func, *self.args, **self.kwds)

    def get_params(self, deep=False):
        return {'func': self.func, 'args': self.args, 'kwds': self.kwds}


class ApplyToDataframe(BaseEstimator, TransformerMixin):

    def __init__(self, func, axis=0, *args, **kwds):
        self.func = func
        self.axis = axis
        self.args = args
        self.kwds = kwds
        super().__init__()

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X.apply(func=self.func, axis=self.axis, *self.args, **self.kwds)

    def get_params(self, deep=False):
        return {'func': self.func, 'axis': self.axis, 'args': self.args, 'kwds': self.kwds}


class ApplyToPandas(BaseEstimator, TransformerMixin):

    def __init__(self, func, axis=None, args=(), **kwds):
        self.func = func
        self.axis = axis
        self.args = args
        self.kwds = kwds
        super().__init__()

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        if self.kwds:
            if self.axis:
                return X.apply(func=self.func, axis=self.axis, args=self.args, **self.kwds)
            else:
                return X.apply(func=self.func, args=self.args, **self.kwds)
        else:
            if self.axis:
                return X.apply(func=self.func, axis=self.axis, args=self.args,)
            else:
                return X.apply(func=self.func, args=self.args)

    def get_params(self, deep=False):
        return {'func': self.func, 'axis': self.axis, 'args': self.args, 'kwds': self.kwds}


class ReshapePandas(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.values.reshape((-1, 1))


class ReshapeNumpy(TransformerMixin):

    def __init__(self, shape):
        self.shape = shape

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X.reshape(self.shape)

    def get_params(self, deep=False):
        return {'shape': self.shape}


class LengthFeature(BaseEstimator, TransformerMixin):

    def __init__(self):
        super().__init__()

    def fit(self, X, y=None):
        return self

    def __length(self, item):
        return len(item)

    def transform(self, X):
        return np.reshape(a=np.array(X.apply(self.__length)), newshape=(-1,1))


class Preprocessor(BaseEstimator, TransformerMixin):

    def __init__(self, preprocessors):
        if isinstance(preprocessors, str):
            raise ValueError('Type {} is invalid for Preprocessor pipeline step. Must be some IPreprocessor.'.format(type(preprocessors)))
        try:
            self.__preps = list(preprocessors)
        except TypeError: # catch when for loop fails
            self.__preps = [preprocessors]

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        for prep in self.__preps:
            X = X.apply(prep.preprocess)
        return X

    def get_params(self, deep=False):
        return {'preprocessors': self.__preps}


class ListPreprocessor(BaseEstimator, TransformerMixin):

    def __init__(self, preprocessors):
        if isinstance(preprocessors, str):
            raise ValueError('Type {} is invalid for ListPreprocessor pipeline step. Must be some IPreprocessor.'.format(type(preprocessors)))
        try:
            self.__preps = list(preprocessors)
        except TypeError: # catch when for loop fails
            self.__preps = [preprocessors]

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        for prep in self.__preps:
            X = X.apply(lambda list_: list(map(prep.preprocess, list_)))
        return X

    def get_params(self, deep=False):
        return {'preprocessors': self.__preps}


class ToSeries(BaseEstimator, TransformerMixin):

    def __init__(self):
        super().__init__()

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        from pandas import Series
        import numpy as np
        if type(X) in (list, tuple, np.array):
            X = Series(X)
        return X

    def get_params(self, deep=False):
        return {}


class ToDataFrame(BaseEstimator, TransformerMixin):

    CATEGORY = 'category'

    def __init__(self, feature_name_map=None, feature_dtype_map=None, learn_categories=False):
        self.names = feature_name_map
        self.dtypes = feature_dtype_map
        self.learn_categories = learn_categories
        super().__init__()

    def __construct_name_list(self, X, y):
        names_list = np.arange(X.shape[1], dtype='O')
        if self.names:
            ids, names = zip(*self.names.items())
            names_list[list(ids)] = names
        self.names_list_ = names_list.tolist()

    def __construct_categories(self, X, y):
        if self.learn_categories and self.dtypes:
            self.categories_map_ = dict()
            for col_name, dtype in self.dtypes.items():
                if dtype == self.CATEGORY:
                    if col_name in self.names_list_:
                        col_index = self.names_list_.index(col_name)
                    else:
                        col_index = col_name
                    self.categories_map_[col_name] = CategoricalDtype(categories=np.unique(X[:,col_index]))

    def fit(self, X, y=None):
        if self.names:
            self.__construct_name_list(X, y)
        if self.learn_categories:
            self.__construct_categories(X, y)
        return self

    def transform(self, X):
        if self.names:
            X = DataFrame(data=X, columns=self.names_list_)
        else:
            X = DataFrame(data=X)
        if self.dtypes:
            for col_name, dtype in self.dtypes.items():
                if dtype == self.CATEGORY:
                    if self.learn_categories:
                        column = Categorical(X.loc[:,col_name].values.tolist(),
                                                dtype=self.categories_map_[col_name])

                    else:
                        column = Categorical(X.loc[:,col_name].values.tolist())
                else:
                    column = X.loc[:,col_name].astype(dtype)
                X.drop(labels=[col_name], axis=1, inplace=True)
                X.loc[:,col_name] = column
        return X

    def get_params(self, deep=False):
        return {'feature_name_map': self.names, 'feature_dtype_map': self.dtypes, 'learn_categories': self.learn_categories}


class PassBy(TransformerMixin):

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X


class CountFeature(TransformerMixin):

    def __init__(self, match_func):
        self.func = match_func
        super().__init__()

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X.apply(self.count_matches).values.reshape((-1,1))

    def count_matches(self, sequence):
        return sum(map(self.func, sequence))


class RelativeCountFeature(TransformerMixin):

    def __init__(self, match_func):
        self.func = match_func
        super().__init__()

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X.apply(self.relative_count).values.reshape((-1,1))

    def relative_count(self, sequence):
        len_ = len(sequence)
        if len_ > 0:
            return self.count_matches(sequence) / len_
        else:
            return 0.0

    def count_matches(self, sequence):
        return sum(self.func(s) for s in sequence)


class Tokenizer(BaseEstimator, TransformerMixin):

    def __init__(self, tokenizer):
        self.__tokenizer = tokenizer

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.apply(self.__tokenizer.tokenize)

    def get_params(self, deep=True):
        return {'tokenizer': self.__tokenizer}


class WSTokenizer(Tokenizer):

    def __init__(self):
        super().__init__(StringWSTokenizer())


class PipeRuleTokenizer(Tokenizer):

    def __init__(self):
        super().__init__(StringRuleTokenizer())


class SpaceDetokenizer(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.apply(' '.join)


class TokenFilterer(BaseEstimator, TransformerMixin):

    def __init__(self, filters):
        if isinstance(filters, str):
            raise ValueError('Type {} is invalid for TokenFilterer pipeline step. Must be some pynlple filter.'.format(type(filters)))
        try:
            self.__filters = list(filters)
        except TypeError: # catch when for loop fails
            self.__filters = [filters]

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        for filt in self.__filters:
            X = X.apply(filt.filter)
        return X

    def get_params(self, deep=False):
        return {'filters': self.__filters}


class TextStatsVectorizer(BaseEstimator, TransformerMixin):
    """Extract features from each document with DictVectorizer"""

    def __init__(self):
        self.vectorizer = DictVectorizer(sparse=False, sort=False)

    def fit(self, X, y=None):
        return self

    def get_feature_names(self):
        return self.vectorizer.feature_names_
    
    def __count_text_stats(self, tokens):
        return {
            'contains_exclamation_point': '!' in tokens,
            'contains_url_tag': 'urltag' in tokens,
            'contains_reference': 'atreftag' in tokens,
            'contains_email': 'emailtag' in tokens,
            'contains_digit': '0' in tokens,
        }

    def transform(self, X):
        return self.vectorizer.fit_transform(X.apply(self.__count_text_stats))


class POSVectorizer(BaseEstimator, TransformerMixin):
    """Extract pos as features from each document with DictVectorizer"""

    def __init__(self):
        import pymorphy2
        self.vectorizer = DictVectorizer(sparse=False, sort=False)
        self.morph = pymorphy2.MorphAnalyzer()
        self.PARTS_OF_SPEECH = frozenset([
            'NOUN',  # имя существительное
            'ADJF',  # имя прилагательное (полное)
            'ADJS',  # имя прилагательное (краткое)
            'COMP',  # компаратив
            'VERB',  # глагол (личная форма)
            'INFN',  # глагол (инфинитив)
            'PRTF',  # причастие (полное)
            'PRTS',  # причастие (краткое)
            'GRND',  # деепричастие
            'NUMR',  # числительное
            'ADVB',  # наречие
            'NPRO',  # местоимение-существительное
            'PRED',  # предикатив
            'PREP',  # предлог
            'CONJ',  # союз
            'PRCL',  # частица
            'INTJ',  # междометие
        ])

    def fit(self, x, y=None):
        return self

    def get_feature_names(self):
        return self.vectorizer.feature_names_

    def __get_pos_count(self, tokens):
        rez = dict.fromkeys(self.PARTS_OF_SPEECH, 0)
        if not tokens or len(tokens) <= 0:
            return rez
        for word in tokens:
            pos = self.morph.parse(word)[0].tag.POS
            if pos:
                rez[pos] += 1
        return {k: v / len(list(tokens)) for k, v in rez.items()}

    def transform(self, X):
        return self.vectorizer.fit_transform(X.apply(self.__get_pos_count))
