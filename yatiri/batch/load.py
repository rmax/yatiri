import csv
import json
import logging

from yatiri import datastore
from yatiri.hashing import doc_guid
from yatiri.keys import get_key


logger = logging.getLogger(__name__)


REQUIRED_FIELDS = (
    'headline',
    'datetime',
    'body',
    'site',
    'url',
)


def parse_domain(url):
    """Returns domain from URL.

    >>> parse_domain("http://www.domain.com/article/123")
    'domain.com'
    >>> parse_domain("https://domain.com/foo-bar")
    'domain.com'

    """
    try:
        head, tail = url.split('://', 1)
    except ValueError:
        raise ValueError("Invalid url {!r}".format(url))
    domain = tail.partition('/')[0]
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain


def preprocess(doc):
    """Add additional fields before storing document.

    >>> doc = preprocess({'url': 'http://foo'})
    >>> 'guid' in doc
    True
    >>> 'url' in doc
    True

    """
    doc['guid'] = doc_guid(doc)
    return doc


def load_csv(stream):
    # read first row as fields
    fields = csv.reader(stream).next()
    if any(f not in fields for f in REQUIRED_FIELDS):
        raise ValueError(
            "Required fields: {}".format(','.join(REQUIRED_FIELDS))
        )
    reader = csv.DictReader(stream, fields)
    # do batch write
    db = datastore.corpus_db()
    with db.write_batch() as wb:
        for n, doc in enumerate(reader, 1):
            doc = preprocess(dict(
                (k, v.decode('utf-8')) for k, v in doc.iteritems()
            ))
            key = get_key(doc)
            wb[key] = doc
        return n


def load_jsonlines(stream):
    # do batch write
    db = datastore.corpus_db()
    with db.write_batch() as wb:
        for n, line in enumerate(stream, 1):
            doc = preprocess(json.loads(line))
            key = get_key(doc)
            wb[key] = doc
        return n
