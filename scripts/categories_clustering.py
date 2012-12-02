#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import itertools
import json
import logging
import math
import numpy as np
import pprint
import xappy


from collections import defaultdict
from nltk.corpus import stopwords as nltk_stopwords
from nltk.tokenize import wordpunct_tokenize
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.feature_extraction.text import (
    TfidfVectorizer, strip_accents_ascii,
    TfidfTransformer, CountVectorizer
)

from yatiri import datastore
from yatiri.batch.load import get_key as get_corpus_key
from yatiri.timing import LogRuntime
from yatiri.classification import default_vectorizer


logger = logging.getLogger(__file__)


def _get_data(category):
    # load data from xapian categories
    db = datastore.corpus_db()
    sconn = xappy.SearchConnection(settings.XAPIAN_DB)
    q = sconn.query_field('category', category)

    offset = 0
    limit = 1000
    while True:
        results = sconn.search(q, offset, offset + limit)

    for key, doc in db.range(key_from, key_to):
        if not any(uri in doc['url'] for uri in DISCARD_URLS):
            yield doc


def get_data(args):
    return filter(None, _get_data(args))



def main(args):
    logger.debug("Arguments: %r", args)
    vect = default_vectorizer()
    vect.set_params(
        ngram_range=(args.min_ngrams, args.max_ngrams),
        max_df=args.max_df,
        max_features=args.max_features,
        sublinear_tf=args.sublinear_tf,
        norm=args.norm,
    )

    with LogRuntime("Loaded input data in {elapsed} seconds", logger):
        data = get_data(args)
    if data:
        logger.debug("Corpus size: {0}".format(len(data)))
    else:
        logger.error("Empty data")
        return

    with LogRuntime("Fitted in {0.elapsed} seconds", logger):
        X = tfidf_vect.fit_transform(data)

    logger.debug("Vocabulary size: {}".format(len(tfidf_vect.vocabulary_)))
    logger.debug("Max DF stop words size: {}".format(len(tfidf_vect.stop_words_)))
    logger.debug("Stop words size: {}".format(len(tfidf_vect.stop_words)))

    if args.clusters:
        true_k = args.clusters
    else:
        # ref: http://en.wikipedia.org/wiki/Determining_the_number_of_clusters_in_a_data_set#Finding_Number_of_Clusters_in_Text_Databases
        m_docs, n_terms = X.shape
        t_nonzeros = len(X.nonzero()[0])
        true_k = (m_docs * n_terms) / t_nonzeros
        logger.debug("Calculated number of clusters: {}".format(true_k))

    if args.minibatch:
        km = MiniBatchKMeans(n_clusters=true_k, init='k-means++', n_init=10,
                             init_size=1000, batch_size=1000, verbose=-1)
    else:
        km = KMeans(n_clusters=args.clusters, init='random', max_iter=100,
                    n_init=10, verbose=1, n_jobs=-1)

    with LogRuntime("KMeans Fitted in {0.elapsed} seconds", logger):
        km.fit(X)

    if args.sample_random and args.sample_size:
        sample = [
            data[i] for i in np.random.random_integers(0, len(data), args.sample_size)
        ]
    elif args.sample_size:
        sample = data[args.sample_skip:args.sample_size]
    else:
        sample = data

    Y = tfidf_vect.transform(sample)
    sample_terms = tfidf_vect.inverse_transform(Y)

    labels = km.predict(Y)
    distances = km.transform(Y)
    center_terms = tfidf_vect.inverse_transform(km.cluster_centers_)

    clusters = defaultdict(list)
    vocabulary = tfidf_vect.vocabulary_

    for i, doc in enumerate(sample):
        clusters[labels[i]].append((i, doc))

    truncate = lambda t: t[:100] + '...' if len(t) > 100 else t

    for label, result in sorted(clusters.iteritems()):
        # skip single results
        if len(result) < args.cluster_minsize:
            continue
        terms_joined = ', '.join(sorted(
            center_terms[label], reverse=True,
            key=lambda t: km.cluster_centers_[label, vocabulary[t]]
        ))
        print '='*79
        print '='*79
        print '='*79
        print '-> ' + truncate(terms_joined) + '\n\n'
        result = sorted(
            result,
            key=lambda (i,_): distances[i,label],
        )

        j = 0
        for i, doc in result:
            j += 1
            doc_terms = ', '.join(sorted(
                sample_terms[i], reverse=True,
                key=lambda t: Y[i, vocabulary[t]],
            ))
            print doc['headline']
            print get_corpus_key(doc)
            print doc['url']
            print 'distance:', distances[i,label]
            print truncate(doc_terms)
            print
            if j > 10:
                print '...'
                break

        print

    if args.shell:
        from IPython import embed; embed()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Clustering",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument('date_from')
    parser.add_argument('date_to')
    parser.add_argument('-f', '--field', dest='fields', nargs='*',
                        default=['headline', 'teaser', 'body'])
    parser.add_argument('-o', '--output')
    parser.add_argument('--shell', action='store_true')

    group = parser.add_argument_group('CountVectorizer parameters')
    group.add_argument('--min-ngrams', type=int, default=1)
    group.add_argument('--max-ngrams', type=int, default=3)
    group.add_argument('--max-df', type=float, default=3.0)
    group.add_argument('--max-features', type=int, default=5000)
    group.add_argument('--sublinear-tf', action='store_true')
    group.add_argument('--binary', action='store_true')
    group.add_argument('--norm', choices=['l1', 'l2'], default='l2')

    group = parser.add_argument_group('KMeans parameters')
    group.add_argument('--minibatch', action='store_true')
    group.add_argument('--clusters', type=int)
    group.add_argument('--sample-size', type=int)
    group.add_argument('--sample-skip', type=int, default=0)
    group.add_argument('--sample-random', action='store_true')
    group.add_argument('--cluster-minsize', type=int, default=1)

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%m:%S %Z',
    )

    main(args)
