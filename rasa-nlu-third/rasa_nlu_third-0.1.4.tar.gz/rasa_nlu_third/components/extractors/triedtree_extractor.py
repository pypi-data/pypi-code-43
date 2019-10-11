# create by fanfan on 2019/9/24 0024
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import warnings

from builtins import str
from typing import Any
from typing import Dict
from typing import Optional
from typing import Text

from rasa.nlu import utils
from rasa.nlu.extractors import EntityExtractor
from rasa.nlu.model import Metadata
from rasa.nlu.training_data import Message, TrainingData

import itertools

from triedTree.patten_tried_tree import PattenTriedTree
from triedTree.entity_tried_tree import EntityTriedTree
import os

class TriedTreeExtractor(EntityExtractor):
    name = "TriedTreeExtractor"
    provides = ["entities"]


    def __init__(self, component_config=None,pattern_tree=None,entity_tree=None):
        # type: (Optional[Dict[Text, Text]]) -> None
        super(TriedTreeExtractor, self).__init__(component_config)
        self.pattern_tree = pattern_tree
        self.entity_tree = entity_tree

    def _load_files(self,data_path):
        entity_files = []
        pattern_files = []
        for root,folders,files in os.walk(data_path):
            for file in files:
                file_path = os.path.join(root,file)
                if 'entity' in file_path or 'modal_words'in file_path :
                    entity_files.append(file_path)
                elif  'intention' in file_path:
                    pattern_files.append(file_path)

        return entity_files,pattern_files

    def train(self, training_data, config, **kwargs):
        entity_files, pattern_files = self._load_files(self.component_config['origin_data'])
        self.entity_tree = EntityTriedTree()
        for file in entity_files:
            self.entity_tree._load_data_tree(file)

        self.pattern_tree = PattenTriedTree()
        for file in pattern_files:
            self.pattern_tree._load_data_tree(file)


    def process(self, message, **kwargs):
        extracted = self.entity_tree.process_with_patten(message.text,self.pattern_tree)
        if  len(extracted['entities']) != 0 :
            message.set("entities", message.get("entities", []) + extracted['entities'], add_to_output=True)
            message.set("intent", extracted['intent'], add_to_output=True)
            message.set("triedTree_match", 1, add_to_output=True)




    def persist(self,filename,model_dir):
        save_model_path = os.path.join(model_dir,self.name)
        if not os.path.exists(save_model_path):
            os.mkdir(save_model_path)

        entity_path = os.path.join(save_model_path, "entity.pkl")
        self.entity_tree.persist(entity_path)

        patten_path = os.path.join(save_model_path, "patten.pkl")
        self.pattern_tree.persist(patten_path)
        return {}

    @classmethod
    def load(cls,
             meta: Dict[Text, Any],
             model_dir=None,  # type: Optional[Text]
             model_metadata=None,  # type: Optional[Metadata]
             cached_component=None,  # type: Optional[Component]
             **kwargs  # type:**Any
             ):
        if model_dir:
            save_model_path = os.path.join(model_dir, cls.name)

            entity_path = os.path.join(save_model_path,"entity.pkl")
            entity_tree = EntityTriedTree()
            entity_tree.restore(entity_path)

            pattern_path = os.path.join(save_model_path,"patten.pkl")
            pattern_tree = PattenTriedTree()
            pattern_tree.restore(pattern_path)
        else:
            entity_tree = None
            pattern_tree = None


        return cls(meta,entity_tree=entity_tree,pattern_tree=pattern_tree)