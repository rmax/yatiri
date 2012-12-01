#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from yatiri.batch.load import load_csv, load_jsonlines
from yatiri.utils import report_progress


EXT_FORMAT = {
    'csv': load_csv,
    'jl': load_jsonlines,
}


def main(args):
    for filepath in args.files:
        try:
            load_func = EXT_FORMAT[filepath.rpartition('.')[-1]]
        except KeyError:
            print "Unrecognized format extension: {}".format(filepath)
        else:
            with open(filepath, 'rb') as fp:
                count = load_func(report_progress(open(filepath, 'rb')))
                print "Loaded {} documents from {}".format(count, filepath)


if __name__ == '__main__':
    from yatiri.log import setup_logging; setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument('files', metavar='datafile', nargs="+")
    args = parser.parse_args()
    main(args)
