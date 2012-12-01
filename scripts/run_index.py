#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging

from yatiri import datastore
from yatiri.batch import search
from yatiri.keys import next_key


logger = logging.getLogger(__file__)


def main(args):
    # index corpus
    db = datastore.corpus_db()
    if args.prefix:
        items = db.range(args.prefix, next_key(args.prefix))
    else:
        items = db.range()
    count = search.index(items, 'corpus', create=args.create)
    print "Indexed {} documents".format(count)


if __name__ == '__main__':
    from yatiri.log import setup_logging; setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument('prefix', nargs='?', help="key prefix")
    parser.add_argument('--create', action='store_true')
    args = parser.parse_args()
    main(args)
