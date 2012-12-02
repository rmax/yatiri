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


def main(args):
    indexer = search.IndexerContext(settings.XAPIAN_DB)
    with indexer as conn:
        search.create_index(conn)

    count = 0
    with indexer as conn, open(args.file) as fp:
        for count, line in enumerate(report_progress(fp)):
            key, cat = line.strip().split('\t')
            cat = eval(cat)
            if isinstance(cat, list):
                cat = cat[0]
            doc = conn.get_document(key)
            doc.add_term('category', cat)
            indexer.conn.replace(doc)

    print "Updated {} documents".format(count)


if __name__ == '__main__':
    from yatiri.log import setup_logging; setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    args = parser.parse_args()
    main(args)
