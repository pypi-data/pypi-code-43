import os
import torch
from torch import nn
from overrides import overrides
from typing import Dict, Any, List
from collections import OrderedDict

import transformers
from transformers.modeling_utils import PreTrainedModel

from vtorch.nn import utils
from vtorch.models import Model
from vtorch.data import Vocabulary
from vtorch.training.metrics import Metric
from vtorch.nn.layers.activation import Activation
from vtorch.common.checks import ConfigurationError


@Model.register("transformer_bert_multilabel_model")
class TransformerMultilabelBert(Model):
    MODEL_NAME = "transformer_bert_multilabel_model"

    def __init__(self, transformer: PreTrainedModel, vocab: Vocabulary, model_params: Dict[str, Any],
                 label_namespace: str = "labels"):
        super().__init__(vocab, label_namespace)
        metrics: Dict[str, Dict[str, Any]] = model_params["metrics"]
        self.metrics: Dict[str, Metric] = {metric_name: Metric.by_name(metric_name)(**metric_params)
                                           for metric_name, metric_params in metrics.items()}
        self.thresholds: torch.Tensor = self._get_tensor_of_thresholds(model_params["thresholds"], vocab,
                                                                       label_namespace)
        self.transformer = transformer
        self.head_dropout = nn.Dropout(model_params["head_dropout"])
        self.classification_head = nn.Linear(model_params["classification_head_size"],
                                             vocab.get_vocab_size(label_namespace))
        self.activation = Activation(model_params["activation"])
        self.loss = nn.BCEWithLogitsLoss()

        self.register_buffer("labels_thresholds", self.thresholds)
        self.register_buffer('one_const_float', torch.tensor([1.]))
        self.register_buffer('zero_const_float', torch.tensor([0.]))
        self.register_buffer('one_const_int', torch.tensor([1]))
        self.register_buffer('zero_const_int', torch.tensor([0]))

    def forward(self, text: torch.Tensor,
                sequence_length: torch.Tensor = None,
                labels: torch.Tensor = None) -> Dict[str, torch.Tensor]:
        attention_mask = torch.where(text == self.zero_const_int, self.zero_const_int, self.one_const_int)
        _, bert_output = self.transformer(text, attention_mask=attention_mask)
        prediction_scores = self.classification_head(self.head_dropout(bert_output))
        logits = self.activation(prediction_scores)
        output = {"logits": logits}
        class_probabilities = self._get_predictions_from_logits(logits)

        if labels is not None:
            output["loss"] = self.loss(prediction_scores, labels)
            for metric in self.metrics.values():
                metric(class_probabilities.float(), labels.float())

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
            raise ConfigurationError("Thresholds keys and labels from vocabulary should be the same size.")
        sorted_vocab_index_token = OrderedDict(sorted(labels_index_token.items()))
        ordered_thresholds = [thresholds[token] for index, token in sorted_vocab_index_token.items()]
        return torch.tensor(ordered_thresholds)

    def _get_predictions_from_logits(self, logits: torch.Tensor) -> torch.Tensor:
        thresholds_with_logits_shape = self.labels_thresholds.repeat(len(logits), 1)
        predictions = torch.where(logits >= thresholds_with_logits_shape,
                                  self.one_const_float,
                                  self.zero_const_float)
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
        transformer_config_path = os.path.join(serialization_dir, "bert_config.json")
        transformer_config = getattr(transformers,
                                     model_params["transformer_config_type"]).from_json_file(
            transformer_config_path)

        model = cls(getattr(transformers,
                            model_params["transformer_model_type"])(transformer_config),
                    vocab=vocab, model_params=model_params)
        model_state = torch.load(weights_file, map_location=utils.device_mapping(cuda_device))
        model.load_state_dict(model_state)

        # Force model to cpu or gpu, as appropriate, to make sure that the embeddings are
        # in sync with the weights
        if cuda_device != -1:
            model.to(cuda_device)

        else:
            model.cpu()

        return model

    @classmethod
    def from_config(cls, config: dict, vocab, cuda_device: int = -1) -> 'Model':
        transformer_model_file_path = os.path.join(config["params"]["transformer_model_name"], "bert_model.pth")
        transformer_config_path = os.path.join(config["params"]["transformer_model_name"], "bert_config.json")
        transformer_config = getattr(transformers,
                                     config["params"]["transformer_config_type"]).from_json_file(
            transformer_config_path)

        model = cls(getattr(transformers,
                            config["params"]["transformer_model_type"]).from_pretrained(transformer_model_file_path,
                                                                                        config=transformer_config),
                    vocab=vocab, model_params=config["params"])
        if cuda_device != -1:
            model.to(cuda_device)

        else:
            model.cpu()

        return model
