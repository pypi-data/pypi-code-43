import argparse
from collections import defaultdict

import torch
from torch.utils import data
from bert_mt_classifier import BertMtClassifier
from data_loader import loadDataset
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import classification_report


def eval(model, iterator, topk):
    model.eval()
    with torch.no_grad():
        all_task = defaultdict(lambda: defaultdict(list))
        for i, batch in enumerate(iterator):
            inputs = batch['input']
            labels = batch['label']
            tasks = batch['task']
            result = model(tasks, inputs, eval=True)
            for index, task in enumerate(tasks):
                res = sorted(result[index], key=result[index].get, reverse=True)
                all_task[task]['pred'].append(res[:topk])
                all_task[task]['true'].append(labels[index].split('/'))
        for k, v in all_task.items():
            print("Task : " + k + " report ")
            mlb = MultiLabelBinarizer().fit(v['true'])
            print(classification_report(mlb.transform(v['true']),
                                        mlb.transform(v['pred']),
                                        target_names=list(mlb.classes_)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="10.pt")
    parser.add_argument("--validset", type=str, nargs='+', default="data/validation.csv")
    parser.add_argument("--batch_size", type=int, default=20)
    parser.add_argument("--bert_model", type=str, default='bert-base-multilingual-uncased')
    parser.add_argument("--topk", type=int, default=1)
    arg = parser.parse_args()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    package = torch.load(arg.model, map_location=device)
    eval_dataset = loadDataset(arg.validset)
    eval_iter = data.DataLoader(dataset=eval_dataset,
                                batch_size=arg.batch_size,
                                shuffle=False)

    if "bert_model" in package:
        bert_model = package['bert_model']
    else:
        bert_model = arg.bert_model
    model = BertMtClassifier(package['task'], bert_model)
    model = model.to(device)
    model.load_state_dict(package['model_state_dict'], strict=False)
    eval(model, eval_iter, arg.topk)
