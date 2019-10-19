import os
import torch
from torch import nn
from overrides import overrides
from typing import Dict, Any, List
from collections import OrderedDict
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence

from vtorch.nn import utils
from vtorch.models import Model
from vtorch.data import Vocabulary
from vtorch.nn.layers.rnn import RNNLayer
from vtorch.training.metrics import Metric
from vtorch.nn.layers.activation import Activation
from vtorch.common.checks import ConfigurationError
from vtorch.nn.layers.aggregation import Aggregation
from vtorch.modules.token_embedders import TokenEmbedder
from vtorch.nn.layers.spacial_dropout import SpacialDropout1d
from vtorch.modules.text_field_embedders import TextFieldEmbedder


@Model.register("mixed_rnn")
class MixedRnn(Model):
    MODEL_NAME = "mixed_rnn"

    def __init__(self, word_embeddings: TextFieldEmbedder, vocab: Vocabulary, model_params: Dict[str, Any],
                 label_namespace: str = "labels"):
        super().__init__(vocab, label_namespace)
        metrics: Dict[str, Dict[str, Any]] = model_params["metrics"]
        self.metrics: Dict[str, Metric] = {metric_name: Metric.by_name(metric_name)(**metric_params)
                                           for metric_name, metric_params in metrics.items()}
        self.thresholds: torch.Tensor = self._get_tensor_of_thresholds(model_params["thresholds"], vocab,
                                                                       label_namespace)
        self.embedding = word_embeddings
        self.embedding_dropout = SpacialDropout1d(model_params["embedding_dropout"])
        self.rnn_1 = RNNLayer.by_name(model_params["rnn_1"]["rnn_type"])(self.embedding.get_output_dim(),
                                                                         hidden_size=model_params["rnn_1"]["hidden_size"],
                                                                         num_layers=model_params["rnn_1"]["hidden_layers"],
                                                                         **model_params["rnn_1"]["additional_params"])

        self.rnn_2 = RNNLayer.by_name(model_params["rnn_2"]["rnn_type"])(self.rnn_1.get_output_dim(),
                                                                         hidden_size=model_params["rnn_2"]["hidden_size"],
                                                                         num_layers=model_params["rnn_2"]["hidden_layers"],
                                                                         **model_params["rnn_2"]["additional_params"])

        self.aggregations = Aggregation(model_params["aggregation_layers"], self.rnn_2.get_output_dim())
        self.predictor = nn.Linear(self.aggregations.get_output_dim(), vocab.get_vocab_size(label_namespace))
        self.activation = Activation(model_params["activation"])
        self.loss = nn.BCEWithLogitsLoss()

        self.register_buffer("labels_thresholds", self.thresholds)
        self.register_buffer('one_const', torch.tensor([1.]))
        self.register_buffer('zero_const', torch.tensor([0.]))

    def forward(self, text: torch.Tensor,
                sequence_length: torch.Tensor = None,
                labels: torch.Tensor = None,
                serial_index: torch.Tensor = None) -> Dict[str, torch.Tensor]:
        embeddings = self.embedding({"text": text})
        embeddings_dropout = self.embedding_dropout(embeddings)
        if sequence_length is not None:
            rnn1_output, _ = self.rnn_1(pack_padded_sequence(embeddings_dropout, sequence_length))
            rnn2_output, _ = self.rnn_2(rnn1_output)
            rnn2_output, _ = pad_packed_sequence(rnn2_output)
        else:
            rnn1_output, _ = self.rnn_1(embeddings_dropout)
            rnn2_output, _ = self.rnn_2(rnn1_output)

        encoder_output = self.aggregations(rnn2_output, sequence_length)
        prediction_scores = self.predictor(encoder_output)
        logits = self.activation(prediction_scores)
        output = {"logits": logits}
        class_probabilities = self._get_predictions_from_logits(logits)

        if labels is not None:
            output["loss"] = self.loss(prediction_scores, labels)
            for metric in self.metrics.values():
                metric(class_probabilities, labels)

        label_names = self._predictions_by_class_to_labelnames(class_probabilities)
        output["label_names"] = label_names
        if serial_index is not None:
            output["serial_index"] = serial_index
        return output

    def get_metrics(self, reset: bool = False) -> Dict[str, float]:
        metrics_to_return = {}
        for model_metric_name, metric in self.metrics.items():
            for metric_name, metric_value in metric.get_metric(reset).items():
                metrics_to_return[metric_name] = metric_value
        return metrics_to_return

    @staticmethod
    def _get_tensor_of_thresholds(thresholds: Dict[str, float],
                                  vocab: Vocabulary,
                                  labels_namespace: str) -> torch.Tensor:
        labels_index_token = vocab.get_index_to_token_vocabulary(labels_namespace)
        if set(thresholds.keys()) != set(labels_index_token.values()):
            raise ConfigurationError("Thresholds keys and labels from vocabulary should be the same.")
        sorted_vocab_index_token = OrderedDict(sorted(labels_index_token.items()))
        ordered_thresholds = [thresholds[token] for index, token in sorted_vocab_index_token.items()]
        return torch.tensor(ordered_thresholds)

    def _get_predictions_from_logits(self, logits: torch.Tensor) -> torch.Tensor:
        thresholds_with_logits_shape = self.labels_thresholds.repeat(len(logits), 1)
        predictions = torch.where(logits >= thresholds_with_logits_shape,
                                  self.one_const,
                                  self.zero_const)
        return predictions

    def _predictions_by_class_to_labelnames(self, predictions_by_class: torch.tensor) -> List[List[str]]:
        instances_labels = [[] for _ in range(len(predictions_by_class))]
        for index_sample, index_label in predictions_by_class.nonzero().tolist():
            instances_labels[index_sample].append(self.vocab.get_token_from_index(index_label, self.labels_namespace))
        return instances_labels

    @classmethod
    @overrides
    def _load(cls,
              model_params: dict,
              serialization_dir: str,
              weights_file: str = None,
              cuda_device: int = -1) -> 'Model':
        vocab = Vocabulary.from_files(os.path.join(serialization_dir, "vocabulary"))
        remove_pretrained_embedding_params(model_params)
        word_embeddings = TextFieldEmbedder.by_name(model_params["word_embeddings"]["type"])(
            {token_name: TokenEmbedder.by_name(list(embedding_type.keys())[0])(**list(embedding_type.values())[0],
                                                                               vocab=vocab,
                                                                               num_embeddings=vocab.get_vocab_size(
                                                                                   token_name))
             for token_name, embedding_type in model_params["word_embeddings"]["token_embedders"].items()})
        model = cls(word_embeddings=word_embeddings, vocab=vocab, model_params=model_params)
        model_state = torch.load(weights_file, map_location=utils.device_mapping(cuda_device))
        model.load_state_dict(model_state)

        # Force model to cpu or gpu, as appropriate, to make sure that the embeddings are
        # in sync with the weights
        if cuda_device >= 0:
            model.cuda(cuda_device)
        else:
            model.cpu()

        return model

    @classmethod
    def from_config(cls, config: dict, vocab, cuda_device: int = -1) -> 'Model':
        word_embeddings = TextFieldEmbedder.by_name(config["params"]["word_embeddings"]["type"])(
            {token_name: TokenEmbedder.by_name(list(embedding_type.keys())[0])(**list(embedding_type.values())[0],
                                                                               vocab=vocab,
                                                                               num_embeddings=vocab.get_vocab_size(token_name))
             for token_name, embedding_type in config["params"]["word_embeddings"]["token_embedders"].items()})
        model = cls(word_embeddings=word_embeddings, vocab=vocab, model_params=config["params"])
        if cuda_device >= 0:
            model.cuda(cuda_device)
        else:
            model.cpu()

        return model


def remove_pretrained_embedding_params(params: dict):
    if 'pretrained_file_path' in params:
        del params['pretrained_file_path']
    for value in params.values():
        if isinstance(value, dict):
            remove_pretrained_embedding_params(value)
