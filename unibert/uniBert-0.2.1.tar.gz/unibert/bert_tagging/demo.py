import argparse
from collections import defaultdict

import torch
from torch.utils import data
from bert_tagging import BertTagger
from data_loader import loadTaggerDataset


def demo(model, sent):
    model.eval()
    with torch.no_grad():
        result = model([sent], eval=True)
        print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="10.pt")
    parser.add_argument("--bert_model", type=str, default='bert-base-multilingual-uncased')
    arg = parser.parse_args()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    package = torch.load(arg.model, map_location=device)
    model = BertTagger(package['labels'], package['bert_model'])
    model = model.to(device)
    model.load_state_dict(package['model_state_dict'], strict=False)

    while True:
        sent = input("Enter a sent : ")
        print(sent)
        demo(model, sent)
