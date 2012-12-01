#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import xappy

from yatiri import datastore, settings
from yatiri.batch import search


logger = logging.getLogger(__file__)


def main(args):
    # search corpus index
    db = datastore.corpus_db()
    sconn = xappy.SearchConnection(settings.XAPIAN_DB)

    query = ' '.join(args.query)

    print "Search {} documents for '{}'".format(
        sconn.get_doccount(), args.query
    )
    results = search.query(sconn, query, args.offset, args.limit)
    if results.estimate_is_exact:
        print "Found {} results".format(results.matches_estimated)
    else:
        print "Found approximately {} results".format(results.matches_estimated)

    for i, result in enumerate(results, 1):
        doc = db[result.id]
        print "{:2}. {}\n\t{}\n\t{}\n".format(i, doc['headline'], doc['url'],
                                             result.id)


if __name__ == '__main__':
    from yatiri.log import setup_logging; setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument('query', nargs="+")
    parser.add_argument('-s', '--offset', type=int, default=0)
    parser.add_argument('-l', '--limit', type=int, default=20)
    args = parser.parse_args()
    main(args)
