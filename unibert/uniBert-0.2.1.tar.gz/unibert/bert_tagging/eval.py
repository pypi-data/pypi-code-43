import argparse
from collections import defaultdict

import torch
from torch.utils import data
from bert_tagging import BertTagger
from data_loader import loadTaggerDataset
from sklearn.metrics import classification_report


def eval(model, iterator):
    model.eval()
    with torch.no_grad():
        all_task = defaultdict(list)
        for i, batch in enumerate(iterator):
            inputs = batch['input']
            labels = batch['label']
            _, result = model(inputs, labels, eval=True)
            for index, task in enumerate(result):
                all_task['pred'].extend([list(v.values())[0] for v in task])
                all_task['true'].extend(labels[index].split(" "))
        print("Report ")
        print(classification_report(all_task['true'],
                                    all_task['pred'],
                                    target_names=model.labels))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="10.pt")
    parser.add_argument("--validset", type=str, nargs='+', default="data/validation.csv")
    parser.add_argument("--batch_size", type=int, default=20)
    parser.add_argument("--bert_model", type=str, default='bert-base-multilingual-uncased')
    arg = parser.parse_args()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    eval_dataset = loadTaggerDataset(arg.validset)
    eval_iter = data.DataLoader(dataset=eval_dataset,
                                batch_size=arg.batch_size,
                                shuffle=False)

    package = torch.load(arg.model, map_location=device)
    model = BertTagger(package['labels'], package['bert_model'])
    model = model.to(device)
    model.load_state_dict(package['model_state_dict'], strict=False)
    eval(model, eval_iter)
