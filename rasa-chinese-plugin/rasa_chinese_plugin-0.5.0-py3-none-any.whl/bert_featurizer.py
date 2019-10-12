# -*- coding: UTF-8 -*-
import logging
import os
import re
from typing import Any, Dict, List, Optional, Text


from rasa_nlu import utils
from rasa_nlu.featurizers import Featurizer
from rasa_nlu.training_data import Message
from rasa_nlu.components import Component
from rasa_nlu.model import Metadata
from rasa_nlu.training_data.training_data import TrainingData
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.tokenizers import jieba_tokenizer

import jieba
from bert_serving.client import ConcurrentBertClient
import numpy as np
from tqdm import tqdm

logger = logging.getLogger(__name__)


class BertFeaturizer(Featurizer):
    provides = []

    requires = []

    defaults = {
        "ip": 'localhost',
        "port": '8125',
        "port_out": '5556',
        "show_server_config": False,
        "output_fmt": 'ndarray',
        "check_version": False,
        "identity": None,
        "batch_size": 128
    }

    language_list = None

    def __init__(self, component_config):
        super(BertFeaturizer, self).__init__(component_config)
        ip = self.component_config['ip']
        port = self.component_config['port']
        port_out = self.component_config['port_out']
        show_server_config = self.component_config['show_server_config']
        output_fmt = self.component_config['output_fmt']
        check_version = self.component_config['check_version']
        timeout = self.component_config['timeout']
        identity = self.component_config['identity']
        self.concurrent_bertClient = ConcurrentBertClient(
                ip = ip,
                port = int(port),
                port_out = int(port_out),
                show_server_config = show_server_config,
                output_fmt = output_fmt,
                check_version = check_version,
                timeout = timeout,
                identity = identity,
                check_length= False
            )

    @classmethod
    def required_packages(cls) -> List[Text]:
        return ["numpy", "bert_serving"]

    @classmethod
    def load(cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Optional["Metadata"] = None,
        cached_component: Optional["Component"] = None,
        **kwargs: Any
        ) -> "Component":
        return cls(meta)


    def _get_message_text(self, messages):
        # all_tokens = [message.data['tokens'] for message in messages]
        all_tokens = [list(jieba.cut(message.text)) for message in messages]
        bert_embedding = self.concurrent_bertClient.encode(all_tokens, is_tokenized=True)
        return np.squeeze(bert_embedding)


    def train(self, training_data: TrainingData, cfg: RasaNLUModelConfig = None, **kwargs: Any) -> None:
        batch_size = self.component_config['batch_size']
        epochs = len(training_data.intent_examples) // batch_size + \
                  int(len(training_data.intent_examples) % batch_size > 0)


        for ep in tqdm(range(epochs), desc="Epochs"):
            end_index = (ep+1) * batch_size
            start_index = ep * batch_size
            examples = training_data.intent_examples[start_index: end_index]
            tokens =  self._get_message_text(examples)
            X = np.array(tokens)

            for index, example in enumerate(examples):
                example.set("text_features", self._combine_with_existing_text_features(example, X[index]))


    def process(self, message: Message, **kwargs) -> None:
        features = self._get_message_text([message])
        message.set("text_features", self._combine_with_existing_text_features(message, features))






