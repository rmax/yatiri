#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import itertools
import json
import logging
import numpy as np
import sys

from sklearn import metrics
from sklearn.datasets import load_files
from sklearn.utils.extmath import density

from yatiri import datastore
from yatiri.classification import (
    build_model_a,
    build_model_b,
    build_model_c,
)
from yatiri.keys import next_key, get_key
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

    report_accuracy(model, categories, test_target, pred)


def report_accuracy(model, categories, test_target, predicted):
    score = metrics.f1_score(test_target, predicted)
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

def load_keys(fromkey, offset, limit):
    tokey = next_key(fromkey)
    db = datastore.corpus_db()
    it = db.range(fromkey, tokey)
    return [v for k,v in itertools.islice(it, offset, offset + limit)]

def main(args):
    dataset = load_docs(args.train_path)

    if args.train_size:
        if args.train_size <= 1:
            train_size = int(args.train_size * len(dataset.data))
        else:
            train_size = int(args.train_size)
    else:
        train_size = len(dataset.data) / 2

    categories = dataset.target_names

    train_data, test_data = split_list(dataset.data, train_size)
    train_target, test_target = split_list(dataset.target, train_size)

    print "{} categories".format(len(categories))
    print "{} documents (training set)".format(len(train_data))

    if args.classify_keys:
        # override test data from given keys
        data = load_keys(args.classify_keys, args.classify_skip,
                         args.classify_limit)
        print "{} documents (classify set)".format(len(data))
        if not data:
            return
        # report results for each model per document
        print 'Models: ' + repr([name for name, _ in MODELS])

        results = []
        for name, model in MODELS:
            # train
            model.fit(train_data, train_target)
            # classify
            pred = model.predict(data)
            results.append(pred)

        for i, doc in enumerate(data):
            print 80 * '-'
            print doc['headline']
            print doc['url']
            print get_key(doc)
            cat_by_model = []
            for j, _ in enumerate(MODELS):
                cat_by_model.append(categories[results[j][i]])
            print 'Result: {!r}'.format(cat_by_model)

        # get top keys
        # v = model.named_steps['vect']
        # X = v.transform([doc])
        # topkeys = [
        #   features[i] for i in np.argsort(row.toarray())[0][-20:]
        # ]
        #from IPython import embed; embed()

    else:
        print "{} documents (testing set)".format(len(test_data))
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
    parser.add_argument('--classify-keys')
    parser.add_argument('--classify-limit', type=int, default=10)
    parser.add_argument('--classify-skip', type=int, default=0)
    args = parser.parse_args()
    main(args)
