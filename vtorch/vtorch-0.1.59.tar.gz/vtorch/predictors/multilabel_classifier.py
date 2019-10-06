from typing import List
from overrides import overrides
from .predictor import Predictor
from vtorch.data import Instance


@Predictor.register("multi_label_classifier")
class MultiLabelClassifier(Predictor):
    def predict(self, inputs: List[Instance]):
        prepared_instances = []
        for sample in inputs:
            prepared_instances.append(
                self._dataset_reader.text_to_instance(text=sample["text"].text if "text" in sample else "",
                                                      labels=sample["labels"].labels if "labels" in sample else None))
        return self.predict_batch_instance(prepared_instances)

    @overrides
    def _json_to_instance(self, json_dict: dict) -> Instance:
        text = json_dict.get("text", "")
        return self._dataset_reader.text_to_instance(text=text)
