#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging

from yatiri import datastore
from yatiri.batch import search
from yatiri.keys import next_key
from yatiri.hashing import doc_guid
from yatiri.utils import report_progress


logger = logging.getLogger(__file__)



def get_classified_items(filepath, db):
    with open(args.from_classified, 'rb') as fp:
        for line in fp:
            key, cat = line.strip().split('\t')
            cat = eval(cat)
            if isinstance(cat, list):
                cat = cat[0]
            doc = db[key]
            doc['guid'] = doc_guid(doc)
            doc['category'] = cat
            if any((f not in doc) for f in ('headline', 'datetime', 'body', 'url')):
                continue
            yield key, doc


def main(args):
    # index corpus
    db = datastore.corpus_db()
    if args.prefix:
        items = db.range(args.prefix, next_key(args.prefix))
    elif args.from_classified:
        items = get_classified_items(args.from_classified, db)
    else:
        items = db.range()
    count = search.index(items, 'corpus', create=args.create)
    print "Indexed {} documents".format(count)


if __name__ == '__main__':
    from yatiri.log import setup_logging; setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument('prefix', nargs='?', help="key prefix")
    parser.add_argument('--create', action='store_true')
    parser.add_argument('--from-classified')
    args = parser.parse_args()
    main(args)
