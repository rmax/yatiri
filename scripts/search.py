#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import xappy

from yatiri import datastore, settings
from yatiri.batch.search import execute_query


logger = logging.getLogger(__file__)


def main(args):
    # search corpus index
    db = datastore.corpus_db()
    sconn = xappy.SearchConnection(settings.XAPIAN_DB)

    query = ' '.join(args.query)

    print "Search {} documents for '{}'".format(
        sconn.get_doccount(), args.query
    )

    q = sconn.query_parse(query, default_op=sconn.OP_AND)

    if args.category:
        qc = q.compose(q.OP_OR, [
            sconn.query_field('category', c) for c in args.category
        ])
        q = q & qc

    if args.date:
        qd = q.compose(q.OP_OR, [
            sconn.query_field('date', d) for d in args.date
        ])
        q = q & qd

    if args.date_start and args.date_end:
        qr = sconn.query_range('date', args.date_start, args.date_end)
        q = q.filter(qr)

    if args.sort:
        sortby = [tuple(args.sort.split(','))]
    else:
        sortby = None

    print 'Query: {!r}'.format(q)
    results = execute_query(sconn, q, args.offset, args.limit,
                            getfacets=args.facet,
                            allowfacets=('category',),
                            sortby=sortby)

    if results.estimate_is_exact:
        print "Found {} results".format(results.matches_estimated)
    else:
        print "Found approximately {} results".format(results.matches_estimated)

    for i, result in enumerate(results, 1):
        doc = db[result.id]
        try:
            cat = result.get_terms('category').next()
        except StopIteration:
            cat = 'none'
        try:
            date = result.get_terms('date').next()
        except StopIteration:
            date = 'none'

        print "{:2}. {} -- {} -- {}\n\t{}\n\t{}\n".format(
            i, cat, doc['headline'], date, doc['url'], result.id)

    from IPython import embed; embed()


if __name__ == '__main__':
    from yatiri.log import setup_logging; setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument('query', nargs="+")
    parser.add_argument('-c', '--category', nargs='*')
    parser.add_argument('-d', '--date', nargs='*')
    parser.add_argument('--date-start')
    parser.add_argument('--date-end')
    parser.add_argument('--facet', action='store_true')
    parser.add_argument('-s', '--offset', type=int, default=0)
    parser.add_argument('-l', '--limit', type=int, default=20)
    parser.add_argument('--sort')
    args = parser.parse_args()
    main(args)
