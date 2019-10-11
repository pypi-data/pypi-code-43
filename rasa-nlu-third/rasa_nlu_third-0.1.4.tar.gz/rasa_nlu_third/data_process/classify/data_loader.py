# create by fanfan on 2019/9/24 0024
import json
import os
import random

import tqdm
from rasa_nlu_third.utils.text_utils import jieba_tokenlization,load_jieba_usedict
class RasaData():
    def __init__(self,folder,min_freq=1,output_path=None,tokenlization=jieba_tokenlization,jieba_dict_path=None):
        self._START_VOCAB = ['[PAD]',  '[UNK]','[CLS]','[SEP]']
        self.folder_path = folder
        self.output_path = output_path
        self.train_folder = os.path.join(self.folder_path, 'train')
        self.test_folder = os.path.join(self.folder_path, 'test')

        self.train_data = []
        self.test_data = []
        self.tokenlization = tokenlization
        if jieba_dict_path != None or jieba_dict_path != "":
            load_jieba_usedict(jieba_dict_path)

    def load_folder_data(self,folder_path):
        total_files = self.getTotalfiles(folder_path)
        for file in tqdm.tqdm(total_files):
            with open(file, 'r', encoding='utf-8') as fr:
                data = json.load(fr)
                for item in data['rasa_nlu_data']['common_examples']:
                    yield self.tokenlization(item['text']), item['intent']

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

        vocab = {}
        for words,label in self.load_folder_data(self.train_folder):
            for word in words:
                if word in vocab:
                    vocab[word] += 1
                else:
                    vocab[word] = 1
            label_list.add(label)


        for words,label in self.load_folder_data(self.test_folder):
            for word in words:
                if word in vocab:
                    vocab[word] += 1
                else:
                    vocab[word] = 1
            label_list.add(label)

        vocab = {key: value for key, value in vocab.items()}
        vocab_list = self._START_VOCAB + sorted(vocab, key=vocab.get, reverse=True)
        vocab_dict = {key: index for index, key in enumerate(vocab_list)}
        label_list = list(label_list)


        if bert_model_path !=None and bert_model_path!= "":
            vocab_list = []
            vocab_path = os.path.join(bert_model_path, 'vocab.txt')
            with open(vocab_path, 'r', encoding='utf-8') as fread:
                for word in fread:
                    vocab_list.append(word.strip())
            vocab_dict = {key: index for index, key in enumerate(vocab_list)}



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



    #def get_train_data(self):
    #    if len(self.train_data) == 0:
    #        for char_and_tag in self.load_folder_data(self.train_folder):
    #            self.train_data.append(char_and_tag)
    #    return self.train_data

    #def get_test_data(self):
    #    if len(self.test_data) == 0:
    #        for char_and_tag in self.load_folder_data(self.test_folder):
    #            self.test_data.append(char_and_tag)
    #    return self.test_data

