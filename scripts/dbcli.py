#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import logging
import sys

from yatiri import datastore
from yatiri.keys import next_key


logger = logging.getLogger(__file__)


def main(args):
    db = getattr(datastore, '{}_db'.format(args.db))()
    if args.command == 'get':
        for key in args.keys:
            print json.dumps(db.get(key))

    elif args.command == 'list':
        for key in args.keys:
            for key in db.range(key, next_key(key), include_value=False):
                print key

    elif args.command == 'list_values':
        for key in args.keys:
            for key, value in db.range(key, next_key(key)):
                print json.dumps(value)

    elif args.command == 'shell':
        from IPython import embed; embed()


if __name__ == '__main__':
    from yatiri.log import setup_logging; setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument('db', choices=['corpus', 'training', 'prod'])
    parser.add_argument('command', choices=[
        'get', 'list', 'list_values', 'shell',
    ])
    parser.add_argument('keys', metavar='key', nargs='+')
    args = parser.parse_args()
    main(args)
