#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging

from yatiri import datastore
from yatiri.keys import next_key


logger = logging.getLogger(__file__)


def main(args):
    db = getattr(datastore, '{}_db'.format(args.db))()
    if args.prefix:
        prefix_from = args.prefix
        prefix_to = next_key(args.prefix)
        it = db.range(prefix_from, prefix_to, include_value=False)
    else:
        it = db.iterkeys()

    # assumes normalized keys with : as separator
    def get_next():
        k = it.next()
        if k.endswith(':'):
            logger.warning("Key with `:` suffix: {!r}".format(k))
            k = k.rstrip(':')
        if k.startswith(':'):
            logger.warning("Key with `:` prefix: {!r}".format(k))
            k = k.lstrip(':')
        bits = k.rpartition(':')
        #logger.debug(bits)
        return bits[0], bits[2]

    try:
        head, tail = get_next()
    except StopIteration:
        print "Empty database"
        return

    if not head:
        # root key
        head = tail

    path = [head]
    count = [1]
    while True:
        try:
            head, tail = get_next()
        except StopIteration:
            while path:
                print '{:10}\t{}'.format(count.pop(), path.pop())
            break
        if head == path[-1]:
            count[-1] += 1
        elif path[-1] in head:
            path.append(head)
            count.append(1)
        else:
            while path:
                prev = path.pop()
                prev_count = count.pop()
                print '{:10}\t{}'.format(prev_count, prev)
                if not path:
                    break
                if path[-1] in head:
                    path.append(head)
                    count.append(1)
            if not path:
                path.append(head)
                count.append(1)


if __name__ == '__main__':
    from yatiri.log import setup_logging; setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument('db', choices=['corpus', 'staging', 'prod'])
    parser.add_argument('prefix', nargs='?')
    args = parser.parse_args()
    main(args)
