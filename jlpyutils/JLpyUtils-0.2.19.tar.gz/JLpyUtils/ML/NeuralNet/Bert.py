"""
Functions/classes using the transformers API from HuggingFaces, which provides a streamlined interface to google's bert model.

Bert: https://github.com/google-research/bert
transformers: https://huggingface.co/transformers/index.html
"""

import torch as _torch
import transformers as _transformers #pytorch_pretrained_bert
from .. import _devices

import sklearn.decomposition as _sklearn_decomposition
import dask.dataframe as _dask_dataframe
import pandas as _pd

class Word2Vec():
    
    def __init__(self, model_ID = 'bert-base-uncased'):
        """
        Use bert to perform word2vect operations on text of interest
        
        Arguments:
        ---------
            model_ID: string. bert model ID.
                - bert-base-uncased: 12-layer, 768-hidden, 12-heads, 110M parameters
                - bert-large-uncased: 24-layer, 1024-hidden, 16-heads, 340M parameters
                - bert-base-cased: 12-layer, 768-hidden, 12-heads , 110M parameters
                - bert-large-cased: 24-layer, 1024-hidden, 16-heads, 340M parameters
        
        Notes:
        ------
            See the article and docs below for a basic walkthrough from which this class was derived
            https://mccormickml.com/2019/05/14/BERT-word-embeddings-tutorial/
            https://huggingface.co/transformers/index.html
        """
        self.model_ID = model_ID
        self.tokenizer = _transformers.BertTokenizer.from_pretrained(model_ID)
    
    def _replace_illegal_chars(self, text):
        for illegal_str in ['-','_','%',',','.',':']:
            text = text.replace(illegal_str, ' ')
        return text
    
    def _insert_transformers_special_tokens(self, text):
        """
        add special ending and starting tokens to text
        """
        return "[CLS] " + text + " [SEP]"
    
    def fit_transform(self, text, verbose = 0):
        """
        Fit and transform the text data of interest. We assume the text is a single "sentence" or a list of different sentence samples
        
        Arguments:
        ----------
            text: a single sentence or a list of sentences
            
        Returns:
        --------
            vect: a vector enconding of length 768
        """
        text = self._replace_illegal_chars(text)
        text = self._insert_transformers_special_tokens(text)
        
        self._tokenized_text = self.tokenizer.tokenize(text)
        self._indexed_tokens = self.tokenizer.convert_tokens_to_ids(self._tokenized_text)
        self._segments_ids = [1] * len(self._indexed_tokens)
        
        # Convert inputs to PyTorch tensors
        self._tokens_tensor = _torch.tensor([self._indexed_tokens])
        self._segments_tensors = _torch.tensor([self._segments_ids])
        
        # Load pre-trained model (weights)
        self.model = _transformers.BertModel.from_pretrained(self.model_ID)

        # Put the model in "evaluation" mode, meaning feed-forward operation.
        self.model.eval()
        
        #check if a gpu is available
        device_counts = _devices.device_counts()
        if device_counts['GPUs']>1:
            self._tokens_tensor = self._tokens_tensor.to('cuda')
            self._segments_tensors = self._segments_tensors.to('cuda')
            self.model.to('cuda')
        
        with _torch.no_grad():
            self.outputs = self.model(self._tokens_tensor, self._segments_tensors)
            self.encoded_layers = self.outputs[0]
            
        self.n_batches = len(self.encoded_layers)
        assert(self.n_batches==1), 'Computed on '+str(self.n_batches)+' batches. Evaluating vector on multiple batches is not supported'
        
        batch_i = 0
        self.n_tokens = len(self.encoded_layers[batch_i])
        
        token_i = 0
        self.n_hidden_units = len(self.encoded_layers[batch_i][token_i])
        
        vect = _torch.mean(self.encoded_layers, 1).tolist()[0]
        
        if self.model_ID == 'bert-base-uncased':
            assert(len(vect)==768), 'len(vect) = '+str(len(vect))+'. Expected len(vect)=768'
        
        return vect
    
    
class Word2VecPCA():
    def __init__(self,
                 n_unique_threshold = 20,
                 PCA_n_components = 0.99,
                 bert_model_ID = 'bert-base-uncased',
                 verbose = 1):
        """
        Vectorizer function which transforms the text based columns in a data frame using the bert word2vec operation, following by PCA to reduce the length of the vector

        Arguments:
        ----------
            n_unique_threshold: integer value defining the minimum number of n_unique values for a given column to warrant word2vecPCA fitting
            PCA_n_components: the n_components returned by the PCA operation after bert's word2vec operation.
                -If 0 < n_components < 1 and svd_solver == 'full', select the number of components such that the amount of variance that needs to be explained is greater than the percentage specified by n_components.
                - See https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html for more details
            bert_model_ID: string. bert model ID of interest.
                - bert-base-uncased: 12-layer, 768-hidden, 12-heads, 110M parameters
                    - bert-large-uncased: 24-layer, 1024-hidden, 16-heads, 340M parameters
                    - bert-base-cased: 12-layer, 768-hidden, 12-heads , 110M parameters
                    - bert-large-cased: 24-layer, 1024-hidden, 16-heads, 340M parameters
            verbose: print-out verbosity
        """

        self.n_unique_threshold = n_unique_threshold
        self.PCA_n_components = PCA_n_components
        self.bert_model_ID = bert_model_ID
        self.BertWord2VecVectorizer = Word2Vec(model_ID=bert_model_ID)
        self.verbose = verbose

        if 'base' in bert_model_ID:
            bert_vect_length = 768
        elif 'large' in bert_model_ID:
            bert_vect_length = 1024

        assert(PCA_n_components<=bert_vect_length), bert_model_ID+' returns vectors of '+str(bert_vect_length)+', choose a PCA_n_components less than or equal to this value.'

    
    def fit_transform(self, df, text_columns = 'auto'):
        """
        Run fit operation on the passed dataframe
        
        Arguments:
        ----------
            df: dataframe to run the fit on
            text_columns: list or 'auto'.
                - If 'auto' the columns of type object or str will be transformed if they have more unique values than the n_unique_threshold parameter
                - If a list is passed, only the columns listed will be considered. The n_unique_threshold criteria will still be evaluated on these columns.
                
                
        Returns:
        --------
            None. The Bert.word2vecPCA object will be updated to allow transform operations.
        """
        
        if type(text_columns)!=type(list()):
            assert(text_columns == 'auto'), 'type(text_columns)='+str(type(text_columns))+'. This not a valid argument. Valid arguments include a list or "auto"'
            text_columns = [col for col in df.columns if df[col].dtype=='O' or df[col].dtype==object]
        else:
            for header in text_columns:
                assert(header in df.columns()), header+' is not in the df passed. Pass a list of valid columns or choose "auto"'
        df = df.copy()
        
        type_df = str(type(df))
        
        if 'dask' in type_df:
            npartitions = df.npartitions
            df = df.compute()
        
        self.BertWord2VecVectorizer_dict = {}
        self.PCAers = {}
        
        for c in range(len(text_columns)):
            col = text_columns[c]
            
            Series = df[col]
                
            Series = Series.fillna('missing')    
            
            texts = list(Series.unique())
            
            if len(texts)>self.n_unique_threshold:
                
                self.BertWord2VecVectorizer_dict[col] = {}

                for t in range(len(texts)):
                    if self.verbose>=1:
                        print('Total Progress:', round((c+1)/len(text_columns)*100,3),'%.',
                              col,'Vectorizing Progress:',round((t+1)/len(texts)*100,3),'%',end='\r')
                    
                    text = texts[t]
                    
                    self.BertWord2VecVectorizer_dict[col][text] = self.BertWord2VecVectorizer.fit_transform(text)
                    
                self.PCAers[col] = _sklearn_decomposition.PCA(n_components=self.PCA_n_components)
                self.PCAers[col].fit([self.BertWord2VecVectorizer_dict[col][text] for text in self.BertWord2VecVectorizer_dict[col].keys()])

                vects = self.PCAers[col].transform([self.BertWord2VecVectorizer_dict[col][text] for text in self.BertWord2VecVectorizer_dict[col].keys()])
                vects = _pd.DataFrame(vects, columns=[col+'_vect'+str(v) for v in range(len(vects[0]))])
                vects[col] = texts
                
                df = _pd.merge(df, vects, on=col)
                df = df.drop(columns = [col])
                
        if self.verbose>=1:
            print('',end='\r')
            
        self.vectorized_columns = list(self.BertWord2VecVectorizer_dict.keys())
        
        if 'dask' in type_df:
            df = _dask_dataframe.from_pandas(df, npartitions = npartitions)
            
        return df
        
    def transform(self, df):
        """
        Run a transform operation after the fit_transform operation has been performed.
        
        Arguments:
        ----------
            df: the dataframe on which the transformation will be applied
        """
        
        df = df.copy()
        
        type_df = str(type(df))
        
        if 'dask' in type_df:
            npartitions = df.npartitions
            df = df.compute()
            
        n_rows = df.shape[0]
        
        for c in range(len(self.vectorized_columns)):
            try:
                col = self.vectorized_columns[c]
                
                try:
                    Series = df[col]
                except Exception as e:
                    display(df)
                    raise Exception(str(e)+' for '+col)
                    
                Series = Series.fillna('missing')    

                texts = list(Series.unique())

                vects = []
                for t in range(len(texts)):

                    print('Total Progress:', round((c+1)/len(self.vectorized_columns)*100,3),'%.',
                              col,'Vectorizing Progress:',round((t+1)/len(texts)*100,3),'%',end='\r')

                    text = texts[t]

                    if text in self.BertWord2VecVectorizer_dict[col].keys():
                        vect = self.BertWord2VecVectorizer_dict[col][text]
                    else:
                        vect = self.BertWord2VecVectorizer.fit_transform(text)
                    vects.append(vect)

                vects = self.PCAers[col].transform(vects)
                vects = _pd.DataFrame(vects, columns=[col+'_vect'+str(v) for v in range(len(vects[0]))])
                vects[col] = texts

                df = _pd.merge(df, vects, on=col)
                df = df.drop(columns = [col])
                
                assert(df.shape[0]==n_rows), 'expected df.shape[0]='+str(n_rows)+' but received '+str(df.shape[0])
            except Exception as e:
                raise Exception(str(e)+' for '+col)
            
        if 'dask' in type_df:
            df = _dask_dataframe.from_pandas(df, npartitions = npartitions)
            
        return df
            
            