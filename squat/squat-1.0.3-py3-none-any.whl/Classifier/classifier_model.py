#!/usr/bin/env python
# coding: utf8
""" Train a convolutional neural network text classifier.

__author__ = "Binay Kumar Ray"
__copyright__ = "Copyright 2019, Binay Kumar Ray"
__version__ = "1.0.0"
__email__ = "binayray2009@gmail.com"
__status__ = "Tool"

Train a convolutional neural network text classifier on the
Bankstatement description classification dataset, using the TextCategorizer component.
The dataset will be loaded automatically via Thinc's built-in dataset loader.
The model is added to spacy.pipeline, and predictions are available via `doc.cats`.
For more details, see the documentation:
* Training: https://spacy.io/usage/training

Compatible with: spaCy v2.0.0+
"""
from __future__ import unicode_literals, print_function
import os
import plac
import random
from pathlib import Path
import thinc.extra.datasets

import spacy
import pandas as pd

from arghandler import ArgumentHandler
from spacy.util import minibatch, compounding


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# @plac.annotations(
#     model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
#     output_dir=("Optional output directory", "option", "o", Path),
#     n_texts=("Number of texts to train from", "option", "t", int),
#     n_iter=("Number of training iterations", "option", "n", int),
#     init_tok2vec=("Pretrained tok2vec weights", "option", "t2v", Path)
# )
def main(model=None, output_dir=None, training_file=None, n_iter=20, n_texts=2000, init_tok2vec=None):
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()

    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank("en")  # create blank Language class
        print("Created blank 'en' model")

    # add the text classifier to the pipeline if it doesn't exist
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if "textcat" not in nlp.pipe_names:
        textcat = nlp.create_pipe(
            "textcat",
            config={
                "exclusive_classes": True,
                "architecture": "simple_cnn",
            }
        )
        nlp.add_pipe(textcat, last=True)
    # otherwise, get it, so we can add labels to it
    else:
        textcat = nlp.get_pipe("textcat")

    # load the Bankstatement description dataset
    print("Loading training data...")
    (train_texts, train_cats), (dev_texts, dev_cats), labels = load_data(training_file=training_file)

    # print(train_cats)
    # add label to text classifier
    for label in labels:
        textcat.add_label(label)

    train_texts = train_texts[:n_texts]
    train_cats = train_cats[:n_texts]
    print(
        "Using {} examples ({} training, {} evaluation)".format(
            n_texts, len(train_texts), len(dev_texts)
        )
    )
    train_data = list(zip(train_texts, [{"cats": cats} for cats in train_cats]))

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "textcat"]
    with nlp.disable_pipes(*other_pipes):  # only train textcat
        optimizer = nlp.begin_training()
        if init_tok2vec is not None:
            with init_tok2vec.open("rb") as file_:
                textcat.model.tok2vec.from_bytes(file_.read())
        print("Training the model...")
        print("{:^5}\t{:^5}\t{:^5}\t{:^5}".format("LOSS", "P", "R", "F"))
        batch_sizes = compounding(4.0, 32.0, 1.001)
        for i in range(n_iter):
            losses = {}
            # batch up the examples using spaCy's minibatch
            random.shuffle(train_data)
            batches = minibatch(train_data, size=batch_sizes)
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, sgd=optimizer, drop=0.2, losses=losses)
            with textcat.model.use_params(optimizer.averages):
                # evaluate on the dev data split off in load_data()
                scores = evaluate(nlp.tokenizer, textcat, dev_texts, dev_cats)
            print(
                "{0:.3f}\t{1:.3f}\t{2:.3f}\t{3:.3f}".format(  # print a simple table
                    losses["textcat"],
                    scores["textcat_p"],
                    scores["textcat_r"],
                    scores["textcat_f"],
                )
            )

    # test the trained model
    test_text = "QUICK CHEQUE DEPOSIT"
    doc = nlp(test_text)
    print(test_text, doc.cats)

    if output_dir is not None:
        with nlp.use_params(optimizer.averages):
            nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        doc2 = nlp2(test_text)
        print(test_text, doc2.cats)


def load_data(limit=0, split=0.8, training_file=None):
    """Load data from the train.csv dataset."""
    # Partition off part of the train data for evaluation
    # import pdb;pdb.set_trace()
    if training_file:
        train_df = pd.read_csv(training_file)
    else:
        train_df = pd.read_csv(os.path.join(BASE_DIR, 'train.csv'))
    grouped_df = train_df.groupby(by='Label')
    csv_labels = grouped_df.groups.keys()
    train_data = [(i[1]['Text'], i[1]['Label']) for i in train_df.iterrows()]
    random.shuffle(train_data)
    train_data = train_data[-limit:]
    texts, labels = zip(*train_data)

    cats = []

    for y in labels:
        v = {k: False for k in csv_labels}
        v[y] = True
        # v = {
        #     'cash': y == 'cash',
        #     'transfer': y == 'transfer',
        #     'salary': y == 'salary',
        #     'tax': y == 'tax',
        #     'digital': y == 'digital',
        #     'shopping': y == 'shopping',
        #     'cheque': y == 'cheque',
        #     'travel': y == 'travel',
        #     'food': y == 'food'
        # }
        cats.append(v)

    # cats = [{"POSITIVE": bool(y), "NEGATIVE": not bool(y)} for y in labels]
    split = int(len(train_data) * split)
    return (texts[:split], cats[:split]), (texts[split:], cats[split:]), csv_labels


def evaluate(tokenizer, textcat, texts, cats):
    docs = (tokenizer(text) for text in texts)
    tp = 0.0  # True positives
    fp = 1e-8  # False positives
    fn = 1e-8  # False negatives
    tn = 0.0  # True negatives
    for i, doc in enumerate(textcat.pipe(docs)):
        gold = cats[i]
        for label, score in doc.cats.items():
            if label not in gold:
                continue
            if score >= 0.5 and gold[label] >= 0.5:
                tp += 1.0
            elif score >= 0.5 and gold[label] < 0.5:
                fp += 1.0
            elif score < 0.5 and gold[label] < 0.5:
                tn += 1
            elif score < 0.5 and gold[label] >= 0.5:
                fn += 1
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    if (precision + recall) == 0:
        f_score = 0.0
    else:
        f_score = 2 * (precision * recall) / (precision + recall)
    return {"textcat_p": precision, "textcat_r": recall, "textcat_f": f_score}


def check_path_validity(path):
    try:
        return os.path.exists(path)
    except:
        return False


def train_classifier_model_cli(parser, context, args):
    """Emit the path to the autocomplete script for use with eval $(snap autocomplete)"""

    handler = ArgumentHandler(usage="Method to train the model",
                              description="Trains the model manually from the cli",
                              epilog="Train the model manually")

    handler.add_argument('-o', '--output', dest='model_path', default='out')

    handler.add_argument('-f', '--file', dest='training_file', default=None)

    out, file = handler.parse_known_args(args)

    if not check_path_validity(out.model_path):
        try:
            os.mkdir(out.model_path)
        except TypeError:
            raise Exception("Please provide a valid path to create the model.")

    if not check_path_validity(out.training_file):
        raise Exception("Training file doesn't exists please provide full path.")

    main(output_dir=out.model_path, training_file=out.training_file)
    # print(out.model_path, out.training_file)


if __name__ == "__main__":
    # plac.call(main)
    output_dir = os.path.join(BASE_DIR, 'out')
    main(output_dir=output_dir)
