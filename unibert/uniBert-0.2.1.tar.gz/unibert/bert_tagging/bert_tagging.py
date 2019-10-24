import math

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
from pytorch_transformers import *
from torch.nn.functional import softmax, sigmoid
from nlp2 import *


class GWLoss(nn.Module):
    def __init__(self):
        super(GWLoss, self).__init__()

    def gaussian(self, x, mean=0.5, variance=0.25):
        for i, v in enumerate(x.data):
            x[i] = math.exp(-(v - mean) ** 2 / (2.0 * variance ** 2))
        return x

    def forward(self, input, target):

        if input.dim() > 2:
            input = input.view(input.size(0), input.size(1), -1)
            input = input.transpose(1, 2)
            input = input.contiguous().view(-1, input.size(2))
        target = target.view(-1, 1)

        logpt = F.log_softmax(input)
        logpt = logpt.gather(1, target)
        logpt = logpt.view(-1)
        pt = Variable(logpt.data.exp())
        loss = -1 * (self.gaussian(pt, variance=0.1 * math.exp(1), mean=0.5) - 0.1 * pt) * logpt
        return loss.mean()


class FocalLoss(nn.Module):
    def __init__(self, gamma=2):
        super(FocalLoss, self).__init__()
        self.gamma = gamma

    def forward(self, input, target):
        if input.dim() > 2:
            input = input.view(input.size(0), input.size(1), -1)  # N,C,H,W => N,C,H*W
            input = input.transpose(1, 2)  # N,C,H*W => N,H*W,C
            input = input.contiguous().view(-1, input.size(2))  # N,H*W,C => N*H*W,C
        target = target.view(-1, 1)

        logpt = F.log_softmax(input)
        logpt = logpt.gather(1, target)
        logpt = logpt.view(-1)
        pt = Variable(logpt.data.exp())

        loss = -1 * (1 - pt) ** self.gamma * logpt
        return loss.mean()


class BertTagger(nn.Module):

    def __init__(self, labels, bert_model="bert-base-multilingual-uncased", dropout=0.2):
        super().__init__()
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print('Using device:', self.device)
        self.tokenizer = BertTokenizer.from_pretrained(bert_model)
        self.bert = BertModel.from_pretrained(bert_model)
        self.dropout = nn.Dropout(dropout)
        self.tagger = nn.Linear(self.bert.config.hidden_size, len(labels))
        self.labels = labels
        self.loss_fct = nn.CrossEntropyLoss()
        # self.loss_fct = FocalLoss()
        # self.loss_fct = GWLoss()

        self.bert = self.bert.to(self.device)
        self.loss_fct = self.loss_fct.to(self.device)

    def forward(self, inputs, targets=None, eval=False):
        result_logits = []
        result_labels = []
        result_items = []
        labels = self.labels
        for id in range(len(inputs)):
            # bert embedding
            if " " not in inputs[id]:
                input = spilt_sentence_to_array(inputs[id], True)
            else:
                input = inputs[id].split(" ")
            input_token = self.tokenizer.tokenize("[CLS] " + inputs[id] + " [SEP]")
            token_input_id = self.tokenizer.convert_tokens_to_ids(input_token)
            token_tesnor = torch.tensor([token_input_id], dtype=torch.long).to(self.device)
            bert_output = self.bert(token_tesnor)
            res = bert_output[0]
            res = torch.mean(res, 0, keepdim=True)
            pooled_output = self.dropout(res)

            # tagger
            tagger_output = self.tagger(pooled_output)
            reshaped_logits = tagger_output.view(-1, len(labels))
            if targets is not None:
                target = targets[id].split(" ")
                target_token = []
                for i, t in zip(input, target):
                    for _ in range(len(self.tokenizer.tokenize(i))):
                        target_token += [labels.index(t)]
                target_token = [labels.index("O")] + target_token + [labels.index("O")]
                # print(list(zip(input_token, target_token)))  # for debug
                tokenize_label = torch.tensor(target_token, dtype=torch.long).to(self.device)
                result_labels.append(tokenize_label)
            result_logits.append(reshaped_logits)
            if eval:
                reshaped_logits = softmax(reshaped_logits)
                logit_prob = reshaped_logits.data.tolist()
                pos = 1  # cls take 0, 1 will be starts
                result_item = []
                for word in input:
                    for _ in range(len(self.tokenizer.tokenize(word))):
                        if _ <= 0:
                            max_index = logit_prob[pos].index(max(logit_prob[pos]))
                            result_item.append({word: labels[max_index]})
                            # print({word: dict(zip(labels, logit_prob[pos]))})
                            # result_item.append({word: dict(zip(labels, logit_prob[pos]))})
                        pos += 1
                # print(result_item)  # for debug
                # print("====")
                result_items.append(result_item)
        # output
        if targets is not None:
            loss = 0
            for i in range(len(result_logits)):
                # print(result_logits[i],result_labels[i],targets[i],inputs[i]) # for debug
                loss += self.loss_fct(result_logits[i], result_labels[i])
            if eval:
                return loss, result_items
            else:
                return loss
        else:
            return result_items
