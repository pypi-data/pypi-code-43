#!/usr/bin/env python
# coding: utf8
"""Utility for SQUAT Text Classifier.

__author__ = "Binay Kumar Ray"
__copyright__ = "Copyright 2019, Binay Kumar Ray"
__version__ = "1.0.0"
__email__ = "binayray2009@gmail.com"
__status__ = "Tool"

This is an utility to use pretrained SQUAT text classifier with the bankstatement,
We do various things like classifying the records onto different labels, summarizing,
calculating sum and avg and other things as well.

For more details on the ML model, see the documentation:
* Training: https://spacy.io/usage/training

Compatible with: spaCy v2.0.0+
"""

import os
import pandas as pd
import re
import spacy
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# from path import path


class ClassifierUtil:
    def __init__(self, statement_data, model_dir=None):
        self.stmt_data = statement_data
        self.total = len(statement_data)

        # loading pretrained model
        if model_dir:
            self.model_dir = model_dir
        else:
            self.model_dir = os.path.join(BASE_DIR, 'out')

        # prepare the saved model and get the categories
        print("Loading from", self.model_dir)
        self.nlp = spacy.load(self.model_dir)
        pipe = self.nlp.get_pipe('textcat')
        self.labels = pipe.labels

        self.stat = {l: [] for l in self.labels}
        self.stat['others'] = []

    def _get_category(self, text):
        """Get the category o the text and accuracy level."""
        pred = self.nlp(text)
        pred_val = max(pred.cats, key=lambda i: pred.cats[i])
        percent_val = pred.cats[pred_val]

        if percent_val >= 0.85:
            accurate = True
        else:
            accurate = False

        return pred_val, percent_val, accurate

    def _update_stat(self, pred_val, record):
        self.stat[pred_val].append(record)

    def evaluate(self):
        """Reset the stat and evaluate everytime all the transactions"""
        self.stat = {l: [] for l in self.labels}
        self.stat['others'] = []
        for record in self.stmt_data.iterrows():
            desc = re.sub('\d', '', record[1]['description'])
            val, percent, accuracy = self._get_category(desc)
            # print(percent, val, record)
            if accuracy: self._update_stat(val, (record[0], record[1]['description']))
            else: self.stat['others'].append((record[0], record[1]['description']))

    def show_stat(self):
        return self.stat

    def _get_month_wise_data(self):
        """Monthwise classfification and calculation."""
        self.stmt_data['date'] = pd.to_datetime(self.stmt_data['date'])
        monthwise_df = self.stmt_data.groupby(self.stmt_data['date'].dt.strftime('%b %Y'))
        months = monthwise_df.groups.keys()
        monthwise_result = {month: {} for month in months}

        for month in months:
            mdf = monthwise_df.get_group(month)
            monthwise_result[month].update(
                {
                    "total_records": len(mdf),
                    "total_cr": mdf['credit'].sum(),
                    "total_dr": mdf['debit'].sum(),
                    "avg_bal": mdf['runningbalance'].mean()
                }
            )

        return monthwise_result

    def get_analysis(self):
        """Get the final result of the analysis."""
        total_cr = self.stmt_data['credit'].sum()
        total_dr = self.stmt_data['debit'].sum()

        d = {
            label: {
                'number': len(self.stat[label]),
                'cr amount': self.stmt_data.loc[[i[0] for i in self.stat[label]], ['credit']].sum().credit,
                'cr_share': self.stmt_data.loc[[i[0] for i in self.stat[label]], ['credit']].sum().credit/total_cr,
                'dr amount': self.stmt_data.loc[[i[0] for i in self.stat[label]], ['debit']].sum().debit,
                'dr_share': self.stmt_data.loc[[i[0] for i in self.stat[label]], ['debit']].sum().debit/total_dr
            }
            for label in self.stat
        }

        d.update(
            {'total_cr': total_cr,
             'total_dr': total_dr,
             'total_records': self.total,
             'statement_period': "{} to {}".format(
                 self.stmt_data['date'].iloc[0],
                 self.stmt_data['date'].iloc[-1],
             ),
             "monthly_data": self._get_month_wise_data()}
        )

        return d


class ClassifierUtilRaw:
    """This is a class designed to get the classification of atext from a pretrained model.
    
    Unlike the previous class you do not need to pass a df but a text just to classify it."""

    def __init__(self, model_dir=None):
        if model_dir:
            self.model_dir = model_dir
        else:
            self.model_dir = os.path.join(BASE_DIR, 'out')

        # prepare the saved model
        print("Loading from", self.model_dir)
        self.nlp = spacy.load(self.model_dir)
        pipe = self.nlp.get_pipe('textcat')
        self.labels = pipe.labels

    def get_cat(self, text):
        pred = self.nlp(text)
        pred_val = max(pred.cats, key=lambda i: pred.cats[i])
        percent_val = pred.cats[pred_val]

        return pred_val, percent_val
