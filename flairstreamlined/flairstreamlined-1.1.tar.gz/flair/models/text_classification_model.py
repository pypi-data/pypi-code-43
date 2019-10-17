import logging
from pathlib import Path
from typing import List, Union

from torch import cat, no_grad, max
from torch.nn import Linear, BCEWithLogitsLoss, CrossEntropyLoss
from torch.nn.functional import softmax as sftmax
from torch.nn.init import xavier_uniform_

from flair.nn import Model
import flair.nn
import flair.embeddings
from flair.data import Dictionary, Sentence, Label
from flair.file_utils import cached_path
from flair.training_utils import store_embeddings

log = logging.getLogger("flair")


class TextClassifier(Model):
    """
    Text Classification Model
    The model takes word embeddings, puts them into an RNN to obtain a text representation, and puts the
    text representation in the end into a linear layer to get the actual class label.
    The model can handle single and multi class data sets.
    """

    def __init__(
        self,
        document_embeddings: flair.embeddings.DocumentEmbeddings,
        label_dictionary: Dictionary,
        multi_label: bool = None,
        multi_label_threshold: float = 0.5,
    ):
        """
        Initializes a TextClassifier
        :param document_embeddings: embeddings used to embed each data point
        :param label_dictionary: dictionary of labels you want to predict
        :param multi_label: auto-detected by default, but you can set this to True to force multi-label prediction
        or False to force single-label prediction
        :param multi_label_threshold: If multi-label you can set the threshold to make predictions
        """

        super(TextClassifier, self).__init__()

        self.document_embeddings: flair.embeddings.DocumentRNNEmbeddings = document_embeddings
        self.label_dictionary: Dictionary = label_dictionary

        if multi_label is not None:
            self.multi_label = multi_label
        else:
            self.multi_label = self.label_dictionary.multi_label

        self.multi_label_threshold = multi_label_threshold

        self.decoder = Linear(
            self.document_embeddings.embedding_length, len(self.label_dictionary)
        )

        self._init_weights()

        if self.multi_label:
            self.loss_function = BCEWithLogitsLoss()
        else:
            self.loss_function = CrossEntropyLoss()

        # auto-spawn on GPU if available
        self.to(flair.device)

    def _init_weights(self):
        xavier_uniform_(self.decoder.weight)

    def forward(self, sentences) -> List[List[float]]:

        self.document_embeddings.embed(sentences)

        text_embedding_list = [
            sentence.get_embedding().unsqueeze(0) for sentence in sentences
        ]
        text_embedding_tensor = cat(text_embedding_list, 0).to(flair.device)

        label_scores = self.decoder(text_embedding_tensor)

        return label_scores

    def _init_model_with_state_dict(state):

        model = TextClassifier(
            document_embeddings=state["document_embeddings"],
            label_dictionary=state["label_dictionary"],
            multi_label=state["multi_label"],
        )

        model.load_state_dict(state["state_dict"])
        return model

    def predict(
        self,
        sentences: Union[Sentence, List[Sentence]],
        mini_batch_size: int = 32,
        embedding_storage_mode="none",
        multi_class_prob: bool = False,
    ) -> List[Sentence]:
        """
        Predicts the class labels for the given sentences. The labels are directly added to the sentences.
        :param sentences: list of sentences
        :param mini_batch_size: mini batch size to use
        :param multi_class_prob : return probability for all class for multiclass
        :return: the list of sentences containing the labels
        """
        with no_grad():
            if type(sentences) is Sentence:
                sentences = [sentences]

            filtered_sentences = self._filter_empty_sentences(sentences)

            # remove previous embeddings
            store_embeddings(filtered_sentences, "none")

            batches = [
                filtered_sentences[x : x + mini_batch_size]
                for x in range(0, len(filtered_sentences), mini_batch_size)
            ]

            for batch in batches:
                scores = self.forward(batch)
                predicted_labels = self._obtain_labels(
                    scores, predict_prob=multi_class_prob
                )

                for (sentence, labels) in zip(batch, predicted_labels):
                    sentence.labels = labels

                # clearing token embeddings to save memory
                store_embeddings(batch, storage_mode=embedding_storage_mode)

            return sentences

    @staticmethod
    def _filter_empty_sentences(sentences: List[Sentence]) -> List[Sentence]:
        filtered_sentences = [sentence for sentence in sentences if sentence.tokens]
        if len(sentences) != len(filtered_sentences):
            log.warning(
                "Ignore {} sentence(s) with no tokens.".format(
                    len(sentences) - len(filtered_sentences)
                )
            )
        return filtered_sentences

    def _obtain_labels(
        self, scores: List[List[float]], predict_prob: bool = False
    ) -> List[List[Label]]:
        """
        Predicts the labels of sentences.
        :param scores: the prediction scores from the model
        :return: list of predicted labels
        """

        if self.multi_label:
            return [self._get_multi_label(s) for s in scores]

        elif predict_prob:
            return [self._predict_label_prob(s) for s in scores]

        return [self._get_single_label(s) for s in scores]

    def _get_single_label(self, label_scores) -> List[Label]:
        softmax = sftmax(label_scores, dim=0)
        conf, idx = max(softmax, 0)
        label = self.label_dictionary.get_item_for_index(idx.item())

        return [Label(label, conf.item())]


    def _predict_label_prob(self, label_scores) -> List[Label]:
        softmax = sftmax(label_scores, dim=0)
        label_probs = []
        for idx, conf in enumerate(softmax):
            label = self.label_dictionary.get_item_for_index(idx)
            label_probs.append(Label(label, conf.item()))
        return label_probs

    def _fetch_model(model_name) -> str:

        model_map = {}
        aws_resource_path = (
            "https://s3.eu-central-1.amazonaws.com/alan-nlp/resources/models-v0.4"
        )

        model_map["de-offensive-language"] = "/".join(
            [
                aws_resource_path,
                "classy-offensive-de-rnn-cuda%3A0",
                "germ-eval-2018-task-1-v0.4.pt",
            ]
        )

        model_map["en-sentiment"] = "/".join(
            [aws_resource_path, "classy-imdb-en-rnn-cuda%3A0", "imdb-v0.4.pt"]
        )

        cache_dir = Path("models")
        if model_name in model_map:
            model_name = cached_path(model_map[model_name], cache_dir=cache_dir)

        return model_name

