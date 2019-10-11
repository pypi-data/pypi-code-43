# create by fanfan on 2019/9/25 0025
import os

import numpy as np
from rasa_nlu_third.utils.ner_data_utils import result_to_json_IBOES

from rasa_nlu_third.tf_models.ner.base_ner_model import BasicNerModel


class Meta_Load():
    def __init__(self,model_dir,use_bert=False,max_sentence_length=None):
        pb_file_path = os.path.join(model_dir, 'ner.pb')
        self.sess, self.input_node,self.input_mask_node, self.output_node = BasicNerModel.load_model_from_pb(pb_file_path)


        self.labels_list = []
        if os.path.exists(os.path.join(model_dir, 'label.txt')):
            with open(os.path.join(model_dir, 'label.txt'), 'r', encoding='utf-8') as fr:
                for line in fr:
                    self.labels_list.append(line.strip())

        self.vocabulary_list = []
        with open(os.path.join(model_dir, 'vocab.txt'), 'r', encoding='utf-8') as fr:
            for line in fr:
                self.vocabulary_list.append(line.strip())

        self.max_sentence_length = max_sentence_length


        self.vocabulary_dict = {value:index for index,value in enumerate(self.vocabulary_list) }
        self.id_2_labels = {index:value for index,value in enumerate(self.labels_list)}
        self.use_IBOES = False
        for item in self.labels_list:
            if "E-" in item:
                self.use_IBOES = True
                break


    def pad_sentence(self,sentence, max_sentence,vocabulary):
        UNK_ID = vocabulary.get('[UNK]')
        PAD_ID = 0
        sentence_batch_ids = [vocabulary.get(w, UNK_ID) for w in sentence]
        if len(sentence_batch_ids) > max_sentence:
            sentence_batch_ids = sentence_batch_ids[:max_sentence]
        else:
            sentence_batch_ids = sentence_batch_ids + [PAD_ID] * (max_sentence - len(sentence_batch_ids))

        if max(sentence_batch_ids) == 0:
            print(sentence_batch_ids)
        return sentence_batch_ids

    def predict(self,text):
        words = ['[CLS]'] + list(text) + ['[SEP]']
        tokens = np.array(self.pad_sentence(words,self.max_sentence_length,self.vocabulary_dict)).reshape((1,self.max_sentence_length))
        text_leng = len(words)
        tokens_mask = []
        for i in range(self.max_sentence_length):
            if i < text_leng:
                tokens_mask.append(1)
            else:
                tokens_mask.append(0)
        tokens_mask = np.array(tokens_mask).reshape((1,self.max_sentence_length))

        predict_ids = self.sess.run(self.output_node, feed_dict={self.input_node: tokens,self.input_mask_node:tokens_mask})
        predict_ids  = predict_ids[0].tolist()[1:len(words) -1]


        if self.use_IBOES:
            entity = result_to_json_IBOES(text,[self.id_2_labels[i] for i in predict_ids])
            return  entity