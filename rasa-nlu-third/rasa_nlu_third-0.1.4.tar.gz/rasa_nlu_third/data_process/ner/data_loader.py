# create by fanfan on 2019/9/24 0024
import json
import os
import random

import tqdm

from rasa_nlu_third.utils import ner_data_utils


class RasaData():
    def __init__(self,folder,tag_schema,min_freq=1,output_path=None):
        self._START_VOCAB = ['[PAD]',  '[UNK]','[CLS]','[SEP]']
        self.folder_path = folder
        self.output_path = output_path
        self.tag_schema = tag_schema
        self.train_folder = os.path.join(self.folder_path, 'train')
        self.test_folder = os.path.join(self.folder_path, 'test')

        self.train_data = []
        self.test_data = []

    def load_folder_data(self,folder_path):
        total_files = self.getTotalfiles(folder_path)
        for file in tqdm.tqdm(total_files):
            with open(file, 'r', encoding='utf-8') as fr:
                data = json.load(fr)
                for item in data['rasa_nlu_data']['common_examples']:
                    entity_offsets = self._convert_example(item)
                    label_and_tag = self._predata(item['text'],entity_offsets)
                    ner_data_utils.update_tag_scheme_singletext(label_and_tag, self.tag_schema)
                    yield label_and_tag

    def getTotalfiles(self,folder_path):
        files = []
        if os.path.isfile(folder_path):
            files.append(folder_path)
        else:
            for file in os.listdir(folder_path):
                files.append(os.path.join(folder_path, file))
        random.shuffle(files)
        return files





    def create_label_dict(self,bert_model_path=None):
        label_list = set()
        for char_and_tag in self.load_folder_data(self.train_folder):
            for word,label in char_and_tag:
                label_list.add(label)

        for char_and_tag in self.load_folder_data(self.test_folder):
            for word, label in char_and_tag:
                label_list.add(label)


        if bert_model_path !=None and bert_model_path!= "":
            vocab_list = []
            vocab_path = os.path.join(bert_model_path, 'vocab.txt')
            with open(vocab_path, 'r', encoding='utf-8') as fread:
                for word in fread:
                    vocab_list.append(word.strip())
            vocab_dict = {key: index for index, key in enumerate(vocab_list)}
        else:
            vocab = {}
            for char_and_tag in self.load_folder_data(self.train_folder):
                for word, label in char_and_tag:
                    if word in vocab:
                        vocab[word] += 1
                    else:
                        vocab[word] = 1
                    label_list.add(label)
                self.train_data.append(char_and_tag)

            for char_and_tag in self.load_folder_data(self.test_folder):
                for word, label in char_and_tag:
                    if word in vocab:
                        vocab[word] += 1
                    else:
                        vocab[word] = 1
                    label_list.add(label)
                self.test_data.append(char_and_tag)

            vocab = {key: value for key, value in vocab.items()}
            vocab_list = self._START_VOCAB + sorted(vocab, key=vocab.get, reverse=True)
            vocab_dict = {key: index for index, key in enumerate(vocab_list)}

        label_list = list(label_list)
        label_list.remove("O")
        label_list = ["O"]+label_list
        if self.output_path != None:
            with open(os.path.join(self.output_path, "vocab.txt"), 'w', encoding='utf-8') as fwrite:
                for word in vocab_list:
                    fwrite.write(word + "\n")

            with open(os.path.join(self.output_path, 'label.txt'), 'w', encoding='utf-8') as fwrite:
                for itent in label_list:
                    fwrite.write(itent + "\n")
        return vocab_dict, vocab_list, label_list

    def load_vocab_and_labels(self):
        vocab_list = []
        labels = []

        with open(os.path.join(self.output_path, "vocab.txt"), 'r', encoding='utf-8') as fread:
            for word in fread:
                vocab_list.append(word.strip())

        with open(os.path.join(self.output_path, 'label.txt'), 'r', encoding='utf-8') as fread:
            for label in fread:
                labels.append(label.strip())

        return {key: index for index, key in enumerate(vocab_list)}, vocab_list, labels

    @staticmethod
    def _convert_example(example):
        def convert_entity(entity):
            return entity["start"], entity["end"], entity["entity"]

        return [convert_entity(ent) for ent in example.get("entities", [])]

    @staticmethod
    def _predata(text, entity_offsets):
        value = 'O'
        bilou = [value for _ in text]
        for (start, end, entity) in entity_offsets:
            if start is not None and end is not None:
                bilou[start] = 'B-' + entity
                for i in range(start + 1, end):
                    bilou[i] = 'I-' + entity
        output = []
        for char,tag in zip(text,bilou):
            output.append([char,tag])
        return output


    def get_train_data(self):
        if len(self.train_data) == 0:
            for char_and_tag in self.load_folder_data(self.train_folder):
                self.train_data.append(char_and_tag)
        return self.train_data

    def get_test_data(self):
        if len(self.test_data) == 0:
            for char_and_tag in self.load_folder_data(self.test_folder):
                self.test_data.append(char_and_tag)
        return self.test_data

