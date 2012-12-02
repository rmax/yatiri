#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import sys

from yatiri import datastore, settings
from yatiri.batch import search
from yatiri.keys import next_key
from yatiri.utils import report_progress


logger = logging.getLogger(__file__)


def get_date(doc):
    date = doc['datetime'].partition(' ')[0]
    if date.count('-') == 2:
        return date


def main(args):
    indexer = search.IndexerContext(settings.XAPIAN_DB)
    with indexer as conn:
        search.create_index(conn)

    count = 0
    db = datastore.corpus_db()
    with indexer as conn:
        for count, key in enumerate(report_progress(conn.iterids())):
            doc = db[key]
            date = get_date(doc)
            if not date:
                continue

            xdoc = conn.get_document(key)
            xdoc.add_term('date', date)
            conn.replace(xdoc)

        print "Updated {} documents".format(count)


if __name__ == '__main__':
    from yatiri.log import setup_logging; setup_logging()
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main(args)
