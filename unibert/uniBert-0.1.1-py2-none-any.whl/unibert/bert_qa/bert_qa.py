import math

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
from pytorch_transformers import *
from torch.nn.functional import softmax, sigmoid
from sklearn.preprocessing import MultiLabelBinarizer
from nlp2 import *


class BCEFocalLoss(nn.Module):
    def __init__(self, gamma=2):
        super(BCEFocalLoss, self).__init__()
        self.gamma = 2

    def forward(self, input, target):
        BCE_loss = F.binary_cross_entropy_with_logits(input, target, reduction='none')
        pt = torch.exp(-BCE_loss)  # prevents nans when probability 0
        focal_loss = (1 - pt) ** self.gamma * BCE_loss
        return focal_loss.mean()


class BCEGWLoss(nn.Module):
    def __init__(self):
        super(BCEGWLoss, self).__init__()

    def gaussian(self, x, mean=0.5, variance=0.25):
        for i, v in enumerate(x.data):
            x.data[i] = math.exp(-(v - mean) ** 2 / (2.0 * variance ** 2))
        return x

    def forward(self, input, target):
        BCE_loss = F.binary_cross_entropy_with_logits(input, target, reduction='none')
        BCE_loss = BCE_loss.view(-1)
        pt = sigmoid(BCE_loss)  # prevents nans when probability 0
        loss = (self.gaussian(pt, variance=0.1 * math.exp(1), mean=0.5) - 0.1 * pt) * BCE_loss
        return loss.mean()


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


class BertMtClassifier(nn.Module):

    def __init__(self, tasks_detail, bert_model="bert-base-chinese", dropout=0.2):
        super().__init__()
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print('Using device:', self.device)
        self.tokenizer = BertTokenizer.from_pretrained(bert_model)
        self.bert = BertModel.from_pretrained(bert_model)
        self.dropout = nn.Dropout(dropout)
        self.loss_fct = nn.CrossEntropyLoss()
        self.loss_fct_mt = BCEFocalLoss()
        # self.loss_fct = FocalLoss()
        # self.loss_fct = GWLoss()

        self.tasks = dict()
        self.tasks_detail = tasks_detail

        self.classifier_list = nn.ModuleList()
        for task, labels in tasks_detail.items():
            self.classifier_list.append(nn.Linear(self.bert.config.hidden_size, len(labels)).to(self.device))
            self.tasks[task] = len(self.classifier_list) - 1

        self.bert = self.bert.to(self.device)
        self.loss_fct = self.loss_fct.to(self.device)
        self.loss_fct_mt = self.loss_fct_mt.to(self.device)

    def forward(self, task, inputs, targets=None, eval=False):
        result_logits = []
        result_labels = []
        result_item = []

        for id in range(len(inputs)):
            task_id = self.tasks[task[id]]
            task_lables = self.tasks_detail[task[id]]
            # bert embedding
            input_token = self.tokenizer.tokenize("[CLS] " + inputs[id] + " [SEP]")
            token_input_id = self.tokenizer.convert_tokens_to_ids(input_token)
            tokenized_input = []
            for i in sliding_widows_larger_step(token_input_id, 256):
                tokenized_input.append(torch.tensor([i], dtype=torch.long).to(self.device))
            res = ""
            for input_pic in tokenized_input:
                output = self.bert(input_pic)
                if isinstance(res, str):
                    res = output[1]
                else:
                    res = torch.cat((res, output[1]), dim=0)
            res = torch.mean(res, 0, keepdim=True)
            pooled_output = self.dropout(res)
            # classifier
            classifier_output = self.classifier_list[task_id](pooled_output)
            logits = torch.sum(classifier_output, dim=0)
            reshaped_logits = classifier_output.view(-1, len(task_lables))
            if targets is not None:
                target = targets[id]
                if 'multi_target' in task[id]:
                    mlb = MultiLabelBinarizer(classes=task_lables)
                    tar = mlb.fit_transform([target.split("/")])
                    tokenize_label = torch.tensor(tar, dtype=torch.float).to(self.device)
                else:
                    tokenize_label = torch.tensor([task_lables.index(target)], dtype=torch.long).to(self.device)
                result_labels.append(tokenize_label)

            result_logits.append(reshaped_logits)
            if 'multi_target' in task[id]:
                reshaped_logits = sigmoid(reshaped_logits)
            else:
                reshaped_logits = softmax(reshaped_logits)
            logit_prob = reshaped_logits[0].data.tolist()
            result_item.append(dict(zip(task_lables, logit_prob)))
        # output
        if targets is not None:
            loss = 0
            for i in range(len(result_logits)):
                if 'multi_target' in task[i]:
                    loss += self.loss_fct_mt(result_logits[i], result_labels[i])
                else:
                    loss += self.loss_fct(result_logits[i], result_labels[i])
            if eval:
                return loss, result_item
            else:
                return loss
        else:
            return result_item
