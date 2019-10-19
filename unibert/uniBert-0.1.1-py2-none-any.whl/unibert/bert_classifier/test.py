import argparse
import csv
from collections import defaultdict

import torch
from torch.utils import data
from bert_mt_classifier import BertMtClassifier
from data_loader import loadDataset


def test(model, iterator, fname):
    task_list = list(model.tasks_detail.keys())
    model.eval()
    with torch.no_grad():
        output_dict = defaultdict(dict)
        for i, batch in enumerate(iterator):
            inputs = batch['input']
            tasks = batch['task']
            result = model(tasks, inputs)
            for i, input in enumerate(inputs):
                output_dict[input][tasks[i]] = max(result[i], key=result[i].get)

    with open(fname, 'w', encoding='utf8', newline='') as csvout:
        writer = csv.writer(csvout, quoting=csv.QUOTE_NONE, quotechar='', escapechar='\\')
        # header
        header = ['input']
        header.extend(task_list)
        writer.writerow(header)
        for input, predict in output_dict.items():
            row = [input] * (len(predict) + 1)
            row[0] = "\"" + row[0] + "\""
            for task, result in predict.items():
                row[task_list.index(task) + 1] = result
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="10.pt")
    parser.add_argument("--test_csv", type=str, nargs='+', default="testing")
    parser.add_argument("--out_csv", type=str, default="test_result.csv")
    parser.add_argument("--bert_model", type=str, default='bert-base-chinese')
    arg = parser.parse_args()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    test_dataset = loadDataset(arg.test_csv)
    test_iter = data.DataLoader(dataset=test_dataset,
                                batch_size=20,
                                shuffle=False)

    package = torch.load(arg.model, map_location=device)
    model = BertMtClassifier(package['task'], arg.bert_model)
    model.to(device)
    model.load_state_dict(package['model_state_dict'])
    test(model, test_iter, arg.out_csv)
