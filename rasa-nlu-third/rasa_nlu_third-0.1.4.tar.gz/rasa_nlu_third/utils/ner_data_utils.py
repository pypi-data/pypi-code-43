# encoding = utf8
import re
import math
import codecs
import random

import numpy as np
import jieba


def create_dict(item_list):
    """
    Create a dictionary of items from a list of list of items.
    """
    assert type(item_list) is list
    dico = {}
    for items in item_list:
        for item in items:
            if item not in dico:
                dico[item] = 1
            else:
                dico[item] += 1
    return dico


def create_mapping(dico):
    """
    Create a mapping (item to ID / ID to item) from a dictionary.
    Items are ordered by decreasing frequency.
    """
    sorted_items = sorted(dico.items(), key=lambda x: (-x[1], x[0]))
    id_to_item = {i: v[0] for i, v in enumerate(sorted_items)}
    item_to_id = {v: k for k, v in id_to_item.items()}
    return item_to_id, id_to_item


def zero_digits(s):
    """
    Replace every digit in a string by a zero.
    """
    return re.sub('\d', '0', s)


def iob2(tags):
    """
    Check that tags have a valid IOB format.
    Tags in IOB1 format are converted to IOB2.
    """
    for i, tag in enumerate(tags):
        if tag == 'O':
            continue
        split = tag.split('-')
        if len(split) != 2 or split[0] not in ['I', 'B']:
            return False
        if split[0] == 'B':
            continue
        elif i == 0 or tags[i - 1] == 'O':  # conversion IOB1 to IOB2
            tags[i] = 'B' + tag[1:]
        elif tags[i - 1][1:] == tag[1:]:
            continue
        else:  # conversion IOB1 to IOB2
            tags[i] = 'B' + tag[1:]
    return True


def iob_iobes(tags):
    """
    IOB -> IOBES
    """
    new_tags = []
    for i, tag in enumerate(tags):
        if tag == 'O':
            new_tags.append(tag)
        elif tag.split('-')[0] == 'B':
            if i + 1 != len(tags) and \
               tags[i + 1].split('-')[0] == 'I':
                new_tags.append(tag)
            else:
                new_tags.append(tag.replace('B-', 'S-'))
        elif tag.split('-')[0] == 'I':
            if i + 1 < len(tags) and \
                    tags[i + 1].split('-')[0] == 'I':
                new_tags.append(tag)
            else:
                new_tags.append(tag.replace('I-', 'E-'))
        else:
            raise Exception('Invalid IOB format!')
    return new_tags


def iobes_iob(tags):
    """
    IOBES -> IOB
    """
    new_tags = []
    for i, tag in enumerate(tags):
        if tag.split('-')[0] == 'B':
            new_tags.append(tag)
        elif tag.split('-')[0] == 'I':
            new_tags.append(tag)
        elif tag.split('-')[0] == 'S':
            new_tags.append(tag.replace('S-', 'B-'))
        elif tag.split('-')[0] == 'E':
            new_tags.append(tag.replace('E-', 'I-'))
        elif tag.split('-')[0] == 'O':
            new_tags.append(tag)
        else:
            raise Exception('Invalid format!')
    return new_tags



def get_seg_features(string):
    """
    Segment text with jieba
    features are represented in bies format
    s donates single word
    """
    seg_feature = []

    for word in jieba.cut(string):
        if len(word) == 1:
            seg_feature.append(0)
        else:
            tmp = [2] * len(word)
            tmp[0] = 1
            tmp[-1] = 3
            seg_feature.extend(tmp)
    return seg_feature


def create_input(data):
    """
    Take sentence data and return an input for
    the training or the evaluation function.
    """
    inputs = list()
    inputs.append(data['chars'])
    inputs.append(data["segs"])
    inputs.append(data['tags'])
    return inputs





def update_tag_scheme_singletext(char_and_tag, tag_scheme):
    """
    Check and update sentences tagging scheme to IOB2.
    Only IOB1 and IOB2 schemes are accepted.
    """
    tags = [w[-1] for w in char_and_tag]
    # Check that tags are given in the IOB format
    if not iob2(tags):
        s_str = '\n'.join(' '.join(w) for w in char_and_tag)
        raise Exception('Sentences should be given in IOB format! ' +
                        'Please check \n%s' % s_str)
    if tag_scheme == 'iob':
        # If format was IOB1, we convert to IOB2
        for word, new_tag in zip(char_and_tag, tags):
            word[-1] = new_tag
    elif tag_scheme == 'iobes':
        new_tags = iob_iobes(tags)
        for word, new_tag in zip(char_and_tag, new_tags):
            word[-1] = new_tag
    else:
        raise Exception('Unknown tagging scheme!')

def input_from_line(line, char_to_id):
    """
    Take sentence data and return an input for
    the training or the evaluation function.
    """

    inputs = list()
    inputs.append([line])
    inputs.append([[char_to_id[char] if char in char_to_id else char_to_id["<UNK>"] for char in line]])
    inputs.append([[]])
    return inputs


class BatchManager(object):

    def __init__(self, data,  batch_size, vocab,tagdict):
        self.batch_size = batch_size
        self.vocab = vocab
        self.tagdict = tagdict
        self.batch_data = self.sort_and_pad(data)
        self.len_data = len(self.batch_data)


    @staticmethod
    def pad_data(data, batcher):
        strings = []
        chars = []
        #segs = []
        targets = []
        crf_labels = []
        max_length = max([len(sentence[0]) for sentence in data])
        for line in data:
            string, char, target,crf_label = line
            padding = ['0'] * (max_length - len(string))
            strings.append(string + padding)
            padding = [0] * (max_length - len(string))
            chars.append(char + padding)
            #segs.append(seg + padding)
            targets.append(target + padding)
            crf_labels.append(crf_label + padding)


        ids = (batcher.batch_sentences(strings))
        return [strings, chars, targets, ids,crf_labels]

    def iter_batch(self, shuffle=False):
        if shuffle:
            random.shuffle(self.batch_data)
        for idx in range(self.len_data):
            yield self.batch_data[idx]







def pad_sentence(sentence, max_sentence_length,vocabulary,label_dict):
    '''
    对batch中的序列进行补全，保证batch中的每行都有相同的sequence_length

    参数：
    - sentence
    '''
    tokens = []
    labels = []
    for token in sentence:
        word_and_type = token.split("\\")
        tokens.append(word_and_type[0])
        if len(word_and_type) == 2:
            labels.append(word_and_type[1])
        else:
            labels.append('O')

            # 序列截断
    if len(tokens) >= max_sentence_length - 1:
        tokens = tokens[0:(max_sentence_length - 2)]
        labels = labels[0:(max_sentence_length - 2)]

    ntokens = []
    segment_ids = []
    label_ids = []

    # 加第一个开始字符
    ntokens.append('[CLS]')
    segment_ids.append(0)
    label_ids.append(0)

    ## 整个句子转换
    for i,token in enumerate(tokens):
        ntokens.append(token)
        segment_ids.append(0)
        label_ids.append(label_dict[labels[i]])

    # 句尾添加[SEP] 标志
    ntokens.append('[SEP]')
    segment_ids.append(0)
    label_ids.append(0)


    unk_id = vocabulary.get('[UNK]')
    input_ids = [vocabulary.get(token,unk_id) for token in ntokens]
    input_mask = [1] * len(input_ids)


    while len(input_ids) < max_sentence_length:
        input_ids.append(0)
        input_mask.append(0)
        segment_ids.append(0)

        # we don't concerned about it!
        label_ids.append(0)
        ntokens.append("**NULL**")

    assert len(input_ids) == max_sentence_length
    assert len(input_mask) == max_sentence_length
    assert len(segment_ids) == max_sentence_length
    assert len(label_ids) == max_sentence_length

    return input_ids,label_ids,segment_ids,input_mask


def pad_sentence_rasa(char_and_label, max_sentence_length,vocabulary,label_dict):
    '''
    对batch中的序列进行补全，保证batch中的每行都有相同的sequence_length

    参数：
    - sentence
    '''


    tokens = [item[0] for item in char_and_label]
    labels = [item[1] for item in char_and_label]
    if len(tokens) >= max_sentence_length - 1:
        tokens = tokens[0:(max_sentence_length - 2)]
        labels = labels[0:(max_sentence_length - 2)]

    ntokens = []
    segment_ids = []
    label_ids = []

    # 加第一个开始字符
    ntokens.append('[CLS]')
    segment_ids.append(0)
    label_ids.append(0)

    ## 整个句子转换
    for i,token in enumerate(tokens):
        ntokens.append(token)
        segment_ids.append(0)
        label_ids.append(label_dict[labels[i]])

    # 句尾添加[SEP] 标志
    ntokens.append('[SEP]')
    segment_ids.append(0)
    label_ids.append(0)


    unk_id = vocabulary.get('[UNK]')
    input_ids = [vocabulary.get(token,unk_id) for token in ntokens]
    input_mask = [1] * len(input_ids)


    while len(input_ids) < max_sentence_length:
        input_ids.append(0)
        input_mask.append(0)
        segment_ids.append(0)

        # we don't concerned about it!
        label_ids.append(0)
        ntokens.append("**NULL**")

    assert len(input_ids) == max_sentence_length
    assert len(input_mask) == max_sentence_length
    assert len(segment_ids) == max_sentence_length
    assert len(label_ids) == max_sentence_length

    return input_ids,label_ids,segment_ids,input_mask


def result_to_json_IBOES(string, tags):
    item = {
        "string": string,
        "entities": []
    }
    entity_name = ""
    entity_start = -1
    current_entity_type = ""
    idx = 0
    for char, tag in zip(string, tags):

        if current_entity_type != "" and tag != "O":
            new_entity_type = tag.replace("B-", "").replace("I-", "").replace("E-","").replace("S-","")
            if new_entity_type != current_entity_type:
                item["entities"].append(
                    {"value": entity_name, "start": entity_start, "end": idx-1, "entity": current_entity_type})
                entity_name = ""
                entity_start = -1
                current_entity_type = ""


        if tag[0] == "B":
            entity_name += char
            entity_start = idx
            current_entity_type = tag.replace("B-", "")
        elif tag[0] == "I":
            entity_name += char
            current_entity_type = tag.replace("I-", "")
        elif tag[0] == "E":
            entity_name += char
            current_entity_type = tag.replace("E-", "")
            item["entities"].append(
                {"value": entity_name, "start": entity_start, "end": idx, "entity": current_entity_type})
            entity_name = ""
            entity_start = -1
            current_entity_type = ""
        elif tag[0] == 'S':
            entity_name = char
            current_entity_type = tag.replace("S-", "")
            item["entities"].append(
                {"value": entity_name, "start": idx, "end": idx  , "entity": current_entity_type})


            entity_name = ""
            entity_start = -1
            current_entity_type = ""
        else:
            if current_entity_type != "" and entity_start != -1:
                item["entities"].append(
                    {"value": entity_name, "start": entity_start, "end": idx -1 , "entity": current_entity_type})
            entity_name = ""
            entity_start = -1
            current_entity_type = ""

        idx += 1

    if current_entity_type != "" and entity_start != -1:
        item["entities"].append(
            {"value": entity_name, "start": entity_start, "end": idx + 1, "entity": current_entity_type})
    return item


