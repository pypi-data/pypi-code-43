import torch
import torch.nn as nn
from pytorch_transformers import *
import numpy as np


class BertOneByOne(nn.Module):
    def __init__(self, bert_model="bert-base-chinese", max_size=128):
        super().__init__()
        self.tokenizer = BertTokenizer.from_pretrained(bert_model)
        self.model = BertForMaskedLM.from_pretrained(bert_model)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.max_size = max_size
        print('Using device:', self.device)
        self.model.to(self.device)

    def forward(self, inputs, targets=None, types=None, masks=None):
        if targets is not None:
            tokens_tensor = torch.tensor(inputs).to(self.device)
            loss_tensors = torch.tensor(targets).to(self.device)
            type_tensors = torch.tensor(types).to(self.device)
            mask_tensors = torch.tensor(masks).to(self.device)
            return self.model(tokens_tensor, token_type_ids=type_tensors, attention_mask=mask_tensors,
                              masked_lm_labels=loss_tensors)
        else:
            tokens_tensor = torch.tensor(inputs).to(self.device)
            type_tensors = torch.tensor(types).to(self.device)
            mask_tensors = torch.tensor(masks).to(self.device)
            return self.model(tokens_tensor.unsqueeze(0), token_type_ids=type_tensors.unsqueeze(0), attention_mask=mask_tensors.unsqueeze(0))

    def get_feature_id_from_input(self, input, target=None):
        row_dict = dict()
        tokenized_input = self.tokenizer.tokenize(input)
        if target is not None:
            tokenized_target = self.tokenizer.tokenize(target)
            tokenized_input.extend(tokenized_target[:-1])
        tokenized_input.append('[MASK]')
        tokenized_input_id = self.tokenizer.convert_tokens_to_ids(tokenized_input)
        mask_id = [1] * len(tokenized_input)
        target_start = len(tokenized_input_id) - 1
        tokenized_input_id.extend([0] * (self.max_size - len(tokenized_input_id)))

        if target is not None:
            tokenized_target_id = [-1] * (len(tokenized_input) - 1)
            tokenized_target_id.append(self.tokenizer.convert_tokens_to_ids([tokenized_target[-1]])[0])
            tokenized_target_id.extend([-1] * (self.max_size - len(tokenized_target_id)))
            row_dict['target'] = np.asarray(tokenized_target_id)

        mask_id.extend([0] * (self.max_size - len(mask_id)))

        type_id = [0] * len(tokenized_input)
        type_id.extend([1] * (self.max_size - len(type_id)))
        row_dict['input'] = np.asarray(tokenized_input_id)
        row_dict['type'] = np.asarray(type_id)
        row_dict['mask'] = np.asarray(mask_id)
        row_dict['start'] = target_start
        return row_dict
