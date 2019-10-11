from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os
import typing

try:
    import cPickle as pickle
except ImportError:
    import pickle

from typing import Any, Optional, Text


from rasa.nlu.components import Component
from rasa.nlu.model import Metadata
from rasa.nlu.training_data import Message


from rasa_nlu_third.tf_models.classifiers.params import Params
from rasa_nlu_third.run_local.classifiers.train import train
from rasa_nlu_third.tf_models.classifiers.pb_loader import Meta_Load
import shutil


logger = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    pass

try:
    import tensorflow as tf
except ImportError:
    tf = None


class DictToObject(object):
    def __init__(self, dict):
        self.__dict__.update(dict)


class EmbeddingIntentClassifierTf(Component):
    name = "EmbeddingIntentClassifierTf"

    provides = ['intent','intent_ranking']

    requires = []

    def __init__(self,component_config=None,pb_meta=None):
        super(EmbeddingIntentClassifierTf, self).__init__(component_config)

        self.component_config = component_config
        self.pb_meta = pb_meta


    def train(self, training_data, config, **kwargs):
        params = Params()
        params.update_dict(self.component_config)
        self.component_config['pb_path'],self.vocab_list,self.label_list = train(params)


    def process(self, message, **kwargs):
        # type: (Message, **Any) -> None
        if message.get('triedTree_match',0) == 0:
            intent_ranking,intent = self.pb_meta.predict(message.text)
            message.set("intent", intent, add_to_output=True)
            #message.set("intent_ranking", intent_ranking, add_to_output=True)

    @classmethod
    def load(cls,
             meta,
             model_dir=None,  # type: Text
             model_metadata=None,  # type: Metadata
             cached_component=None,  # type: Optional[Component]
             **kwargs  # type: **Any
             ):
        if model_dir:
            save_model_path = os.path.join(model_dir, cls.name)
            pb_meta_load = Meta_Load(model_dir=save_model_path,use_bert=meta['use_bert'],max_sentence_length=meta['max_sentence_length'])
            return EmbeddingIntentClassifierTf(component_config=meta,pb_meta=pb_meta_load)

    def persist(self,filename,model_dir):
        save_model_path = os.path.join(model_dir,self.name)
        if not os.path.exists(save_model_path):
            os.mkdir(save_model_path)
        with open(os.path.join(save_model_path,'label.txt'),'w',encoding='utf-8') as fwrite:
            for label in self.label_list:
                fwrite.write(label + "\n")

        with open(os.path.join(save_model_path,'vocab.txt'),'w',encoding='utf-8') as fwrite:
            for word in self.vocab_list:
                fwrite.write(word + "\n")

        save_pb_path = os.path.join(save_model_path,'classify.pb')
        shutil.copy(self.component_config['pb_path'],save_pb_path)
        return {"classifier_file":save_pb_path}
