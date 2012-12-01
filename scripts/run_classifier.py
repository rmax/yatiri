#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import cmd
import itertools
import json
import logging
import numpy as np
import os
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
from yatiri.hashing import doc_guid
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


class LabelValidation(cmd.Cmd):

    prompt_fmt = '({0.current}/{0.total}) '

    def __init__(self, train_path, results):
        cmd.Cmd.__init__(self)
        self.train_path = train_path
        self.current = 0
        self.total = len(results)
        self.results = iter(results)

    def preloop(self):
        self.do_next('')

    def do_next(self, line):
        """Go next document"""
        try:
            self.current_doc, self.current_label = self.results.next()
        except StopIteration:
            print "No more documents"
            return True

        self.current += 1
        self.prompt = self.prompt_fmt.format(self)
        self.do_print(line)

    do_n = do_next

    def do_print(self, line):
        """View summary"""
        print "\t" + self.current_doc['headline']
        print "\t{!r}".format(self.current_label)

    do_p = do_print

    def do_view(self, line):
        """View document"""
        if line:
            try:
                limit = int(line)
            except ValueError:
                print "*** Invalid integer"
                return
        else:
            limit = 500

        print get_key(self.current_doc)
        print self.current_doc['headline']
        print self.current_doc['url']
        print

        if len(self.current_doc['body']) > limit:
            print self.current_doc['body'][:limit] + '...'
        else:
            print self.current_doc['body']

    do_v = do_view

    def do_label(self, line):
        """Update label for current document storing it
        in the train_path.
        """
        label = line.strip()
        path = os.path.join(self.train_path, label)
        if not os.path.exists(path):
            os.mkdir(path)
        filepath = os.path.join(path, doc_guid(self.current_doc) + '.json')
        with open(filepath, 'wb') as fp:
            json.dump(self.current_doc, fp)
        print "Document stored in train category {}".format(label)
        print "Moving to next document"
        return self.do_next('')

    do_l = do_label

    def complete_label(self, text, line, begidx, endidx):
        categories = os.listdir(self.train_path)
        if text:
            return [cat for cat in categories if cat.startswith(text)]
        else:
            return categories

    complete_l = complete_label

    def do_quit(self, line):
        """Quit"""
        return True

    do_q = do_quit

    def do_EOF(self, line):
        return True




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

        labels = []
        for i, doc in enumerate(data):
            _by_model = []
            for j, _ in enumerate(MODELS):
                _by_model.append(categories[results[j][i]])
            labels.append(_by_model)

        data_labels = zip(data, labels)
        LabelValidation(args.train_path, data_labels).cmdloop()

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
