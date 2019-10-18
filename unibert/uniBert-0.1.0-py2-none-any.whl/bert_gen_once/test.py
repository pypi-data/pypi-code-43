import torch
import torch.nn as nn
from bert_gen_once import BertOnce


def test(model_path, inputs):
    bertmodel = BertOnce()
    model = nn.DataParallel(bertmodel)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    with torch.no_grad():
        predictions = model(inputs)
    input = "[CLS] " + inputs[0] + " [SEP]"
    start = len(bertmodel.tokenizer.tokenize(input))
    while start < len(predictions[0]):
        predicted_index = torch.argmax(predictions[0, start]).item()
        predicted_token = bertmodel.tokenizer.convert_ids_to_tokens([predicted_index])
        if '[SEP]' in predicted_token:
            break
        print(predicted_token)
        start += 1


test("./exper/30.pt", ["wi di gu shi bao di"])
