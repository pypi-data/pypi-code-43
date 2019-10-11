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

from rasa.nlu.extractors import EntityExtractor
from rasa.nlu.model import Metadata
from rasa.nlu.training_data import Message


from rasa_nlu_third.tf_models.ner.params import Params
from rasa_nlu_third.run_local.ner.train import train
from rasa_nlu_third.tf_models.ner.pb_loader import Meta_Load
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


class TfEntityExtractor(EntityExtractor):
    name = "TfEntityExtractor"

    provides = ["entities"]

    requires = []

    def __init__(self,component_config=None,pb_meta=None):
        super(TfEntityExtractor, self).__init__(component_config)

        self.component_config = component_config
        self.pb_meta = pb_meta

    def normal_train(self,params):
        self.component_config['pb_path'] = train(params)


    def train(self, training_data, config, **kwargs):
        params = Params()
        params.update_dict(self.component_config)
        self.component_config['pb_path'],self.vocab_list,self.label_list = train(params)


    def process(self, message, **kwargs):
        # type: (Message, **Any) -> None
        if message.get('triedTree_match',0) == 0:
            extracted = self.pb_meta.predict(message.text)
            message.set("entities", message.get("entities", []) + extracted['entities'], add_to_output=True)

    @classmethod
    def load(cls,
             meta,
             model_dir=None,  # type: Text
             model_metadata=None,  # type: Metadata
             cached_component=None,  # type: Optional[CRFEntityExtractor]
             **kwargs  # type: **Any
             ):
        if model_dir:
            save_model_path = os.path.join(model_dir, cls.name)
            pb_meta_load = Meta_Load(model_dir=save_model_path,use_bert=meta['use_bert'],max_sentence_length=meta['max_sentence_length'])
            return TfEntityExtractor(component_config=meta,pb_meta=pb_meta_load)

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

        save_pb_path = os.path.join(save_model_path,'ner.pb')
        shutil.copy(self.component_config['pb_path'],save_pb_path)
        return {"ner_file":save_pb_path}
