import torch as _torch
import pytorch_pretrained_bert as _bert

class word2vect():
    
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
            See the article below for a basic walkthrough from which this class was derived
            https://mccormickml.com/2019/05/14/BERT-word-embeddings-tutorial/
        """
        self.model_ID = model_ID
        self.tokenizer = _bert.BertTokenizer.from_pretrained(model_ID)
        
    def _insert_bert_special_tokens(self, text):
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

        text = self._insert_bert_special_tokens(text)
        
        self._tokenized_text = self.tokenizer.tokenize(text)
        self._indexed_tokens = self.tokenizer.convert_tokens_to_ids(self._tokenized_text)
        self._segments_ids = [1] * len(self._indexed_tokens)
        
        # Convert inputs to PyTorch tensors
        self._tokens_tensor = _torch.tensor([self._indexed_tokens])
        self._segments_tensors = _torch.tensor([self._segments_ids])

        # Load pre-trained model (weights)
        self.model = _bert.BertModel.from_pretrained(self.model_ID)

        # Put the model in "evaluation" mode, meaning feed-forward operation.
        self.model.eval()
        
        with _torch.no_grad():
            self.encoded_layers, _ = self.model(self._tokens_tensor, self._segments_tensors)
           
        vect = _torch.mean(self.encoded_layers[-1], 1).tolist()[0]
        
        return vect