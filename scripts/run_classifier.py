#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import logging
import numpy as np
import sys

from sklearn import metrics
from sklearn.datasets import load_files
from sklearn.utils.extmath import density

from yatiri.classification import (
    build_model_a,
    build_model_b,
    build_model_c,
)
from yatiri.timing import WriteRuntime


logger = logging.getLogger(__file__)


MODELS = (
    ('base', build_model_a()),
    ('chi2select', build_model_b()),
    ('multifeature', build_model_c()),
)

# test parameters
PARAMETERS = {
    'base': {
        'vect__max_df': 0.5,
        'vect__min_df': 3,
        'vect__ngram_range': (1,4),
    },
    'chi2select': {
        'vect__max_df': 0.5,
        'vect__min_df': 3,
        'vect__ngram_range': (1,4),
    },
    'multifeature': {
        #'vect__title__max_df': 1,
        #'vect__title__min_df': 1,
        'vect__title__ngram_range': (1,2),
        'vect__body__max_df': .5,
        'vect__body__min_df': 3,
        'vect__body__ngram_range': (1,4),
        'clf__n_jobs': 4,
    },
}


def split_list(list_, length):
    return list_[:length], list_[length:]


def benchmark(model, categories, train_data, train_target, test_data, test_target):
    print 80 * '-'
    print "Training: {}".format(repr(model)[:70])

    with WriteRuntime("train time: {elapsed:.3f}\n", sys.stdout):
        model.fit(train_data, train_target)

    with WriteRuntime("test time: {elapsed:.3f}\n", sys.stdout):
        pred = model.predict(test_data)

    score = metrics.f1_score(test_target, pred)
    print "f1-score: {:.3f}".format(score)

    coef = model.named_steps['clf'].coef_
    print "dimensionality: {}".format(coef.shape[1])
    print "density: {}".format(density(coef))

    print "top 20 keywords per class:"
    feature_names = np.asarray(model.named_steps['vect'].get_feature_names())
    for i, category in enumerate(categories):
        topkw = np.argsort(coef[i])[-20:]
        print "{}: {}".format(category, ", ".join(feature_names[topkw]))
    print

    print "classification report:"
    print metrics.classification_report(test_target, pred,
                                        target_names=categories)

    print "confusion matrix:"
    print metrics.confusion_matrix(test_target, pred)
    print


def load_docs(path):
    dataset = load_files(args.train_path)
    docs = []
    for raw_data in dataset.data:
        docs.append(json.loads(raw_data))
    dataset.data = docs
    return dataset


def main(args):
    dataset = load_docs(args.train_path)

    if args.train_size:
        if args.train_size < 1:
            train_size = int(args.train_size * len(dataset.data))
        else:
            train_size = int(args.train_size)
    else:
        train_size = len(dataset.data) / 2

    categories = dataset.target_names
    train_data, test_data = split_list(dataset.data, train_size)
    train_target, test_target = split_list(dataset.target, train_size)

    print "{} documents (training set)".format(len(train_data))
    print "{} documents (testing set)".format(len(test_data))
    print "{} categories".format(len(categories))

    results = []
    params = (categories, train_data, train_target, test_data, test_target)
    for name, model in MODELS:
        print (80 * '=')
        print name
        model.set_params(**PARAMETERS[name])
        results.append(benchmark(model, *params))



if __name__ == '__main__':
    from yatiri.log import setup_logging; setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument('train_path')
    parser.add_argument('--train-size', type=float)
    args = parser.parse_args()
    main(args)
