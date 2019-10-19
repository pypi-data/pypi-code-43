import torch
import torch.nn as nn
from torch.nn.functional import softmax

from bert_onebyone import BertOneByOne


def test(model_path, input):
    max_size = 300
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    bertmodel = BertOneByOne(bert_model="bert-base-chinese")
    bertmodel.to(device)
    bertmodel = nn.DataParallel(bertmodel)
    bertmodel.load_state_dict(torch.load(model_path, map_location=device))
    bertmodel = bertmodel.module
    bertmodel.eval()
    with torch.no_grad():
        output = ""
        while len(output) < 300:
            feature_dict = bertmodel.get_feature_id_from_input(input + ' [SEP] ' + output)
            predictions = bertmodel(feature_dict['input'],
                                    types=feature_dict['type'],
                                    masks=feature_dict['mask'])
            predicted_index = torch.argmax(predictions[0, feature_dict['start']]).item()
            predicted_token = bertmodel.tokenizer.convert_ids_to_tokens([predicted_index])
            print(predicted_token)
            logit_prob = softmax(predictions[0, feature_dict['start']]).data.tolist()
            prob_result = {bertmodel.tokenizer.ids_to_tokens[id]: prob for id, prob in enumerate(logit_prob)}
            prob_dict = sorted(prob_result.items(), key=lambda x: x[1], reverse=True)
            print(prob_dict[:5])
            if '[SEP]' in predicted_token:
                break
            output += predicted_token[0]
        print(output)


test("../checkpoints/22.pt", "lin dai chao a ji")
