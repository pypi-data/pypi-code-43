import argparse
import torch
import torch.nn as nn
import tensorboardX as tensorboard
from bert_gen_once import *
from unibert.bert_gen_onebyone import *
from torch.utils import data
from bert_classifier import *
from sklearn.metrics import classification_report
from sklearn.preprocessing import MultiLabelBinarizer


def write_log(*args):
    line = ' '.join([str(a) for a in args])
    with open(os.path.join(arg.savedir, "message.log"), "a", encoding='utf8') as log_file:
        log_file.write(line + '\n')
    print(line)


def optimizer(model, arg):
    param_optimizer = list(model.named_parameters())
    param_optimizer = [n for n in param_optimizer if 'pooler' not in n[0]]
    no_decay = ['bias', 'gamma', 'beta', 'LayerNorm.bias', 'LayerNorm.weight']
    optimizer_parameters = [
        {'params': [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)], 'weight_decay_rate': 0.01},
        {'params': [p for n, p in param_optimizer if any(nd in n for nd in no_decay)], 'weight_decay_rate': 0.0}
    ]
    # optimizer = torch.optim.Adamax(optimizer_parameters, lr=arg.lr)
    optimizer = torch.optim.Adamax(model.parameters(), lr=arg.lr)
    return optimizer


def train(model, iterator, arg, fname):
    model = nn.DataParallel(model)
    optim = optimizer(model, arg)
    t_loss = 0
    model.train()
    for i, batch in enumerate(iterator):
        if 'classifier' in arg.model:
            loss = model(batch['task'], batch['input'], batch['label'])
        else:
            output = model(batch['input'], batch['target'], batch['type'], batch['mask'])
            loss = output[0]
        optim.zero_grad()
        loss.mean().backward()
        optim.step()
        t_loss += loss.mean().item()

        if arg.tensorboard:
            writer.add_scalar("loss/step", loss.mean().item(), epoch)
        if i % 100 == 0 and i != 0:  # monitoring
            write_log(f"step: {i}, loss: {t_loss / (i + 1)}, total: {len(iterator)}")

    write_log(f"step: {len(iterator)}, loss: {t_loss / len(iterator)}, total: {len(iterator)}")
    return t_loss / len(iterator)


def eval(model, iterator, fname):
    model.eval()
    t_loss = 0
    with torch.no_grad():
        all_task = defaultdict(lambda: defaultdict(list))
        for i, batch in enumerate(iterator):
            if 'classifier' in arg.model:
                inputs = batch['input']
                labels = batch['label']
                tasks = batch['task']
                loss, result = model(tasks, inputs, labels, eval=True)
                for index, task in enumerate(tasks):
                    if 'multi_target' in task:
                        all_task[task]['pred'].append([k for (k, v) in result[index].items() if v >= 0.5])
                        all_task[task]['true'].append(labels[index].split("/"))
                    else:
                        all_task[task]['pred'].append(max(result[index], key=result[index].get))
                        all_task[task]['true'].append([labels[index]])
            else:
                output = model(batch['input'], batch['target'], batch['type'], batch['mask'])
                loss = output[0]
            t_loss += loss.mean().item()
    avg_t_loss = t_loss / len(iterator)

    write_log(f"model: {fname}, Total Loss: {avg_t_loss}")
    if 'classifier' in arg.model:
        for k, v in all_task.items():
            write_log("Task : " + k + " report ")
            mlb = MultiLabelBinarizer().fit(v['true'])
            write_log(classification_report(mlb.transform(v['true']),
                                            mlb.transform(v['pred']),
                                            target_names=list(mlb.classes_)))
    if arg.tensorboard:
        writer.add_scalar("eval_loss/step", avg_t_loss, epoch)
    return avg_t_loss


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, default=50)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument("--epoch", type=int, default=30)
    parser.add_argument("--maxlen", type=int, default=128)
    parser.add_argument("--savedir", type=str, default="checkpoints/")
    parser.add_argument("--train", type=str, nargs='+', default="train.csv", required=True)
    parser.add_argument("--valid", type=str, nargs='+', default="valid.csv", required=True)
    parser.add_argument("--model", type=str, default="once", choices=['once', 'onebyone', 'classifier'])
    parser.add_argument("--bert", type=str, default='bert-base-multilingual-uncased',
                        help='bert-base-multilingual-uncased/bert-base-chinese')
    parser.add_argument("--worker", type=int, default=8)
    parser.add_argument('--tensorboard', dest='tensorboard', action='store_true', help='Turn on tensorboard graphing')
    parser.add_argument("--resume")
    arg = parser.parse_args()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    if not os.path.exists(arg.savedir): os.makedirs(arg.savedir)

    if "once" in arg.model:
        model = BertOnce(bert_model=arg.bert, max_size=arg.maxlen)
        train_dataset = loadOnceDataset(arg.train[0], model)
        eval_dataset = loadOnceDataset(arg.valid[0], model)
    elif "onebyone" in arg.model:
        model = BertOneByOne(bert_model=arg.bert, max_size=arg.maxlen)
        train_dataset = loadOneByOneDataset(arg.train[0], model)
        eval_dataset = loadOneByOneDataset(arg.valid[0], model)
    elif 'classifier' in arg.model:
        train_dataset = loadDataset(arg.train)
        eval_dataset = loadDataset(arg.valid)
        model = BertMtClassifier(train_dataset.task, arg.bert)

    if arg.tensorboard:
        writer = tensorboard.SummaryWriter()

    if arg.resume is not None:
        package = torch.load(arg.resume, map_location=device)
        if 'model_state_dict' in package:
            model.load_state_dict(package['model_state_dict'])
        else:
            model.load_state_dict(package)
        start_epoch = int(package.get('epoch', 1)) - 1

    train_iter = data.DataLoader(dataset=train_dataset,
                                 batch_size=arg.batch,
                                 shuffle=True,
                                 num_workers=arg.worker)

    eval_iter = data.DataLoader(dataset=eval_dataset,
                                batch_size=arg.batch,
                                shuffle=False,
                                num_workers=arg.worker)

    write_log("batch : " + str(arg.batch))
    train_loss_results = dict()
    eval_loss_results = dict()
    for epoch in range(1, arg.epoch + 1):
        fname = os.path.join(arg.savedir, str(epoch))
        print(f"=========train at epoch={epoch}=========")
        train_avg_loss = train(model, train_iter, arg, fname)

        print(f"=========eval at epoch={epoch}=========")
        eval_avg_loss = eval(model, eval_iter, fname)

        if arg.tensorboard:
            writer.add_scalar("train_loss/epoch", train_avg_loss, epoch)
            writer.add_scalar("eval_loss/epoch", eval_avg_loss, epoch)

        if 'classifier' in arg.model:
            torch.save({
                'model_state_dict': model.state_dict(),
                'task': train_dataset.task,
                'bert_model': arg.bert
            }, f"{fname}.pt")
        else:
            torch.save(model.state_dict(), f"{fname}.pt")

        print(f"weights were saved to {fname}.pt")
