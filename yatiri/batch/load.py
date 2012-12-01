import csv
import json
import logging

from yatiri import datastore
from yatiri.hashing import doc_guid


logger = logging.getLogger(__name__)


REQUIRED_FIELDS = (
    'headline',
    'datetime',
    'body',
    'site',
    'url',
)

KEY_FORMAT = 'news:{year}{month}{day}:{site}:{guid}'


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


def get_key(doc):
    """Returns unique key for given document.

    >>> doc1 = dict(guid='1', datetime='2012-11-29', site='a')
    >>> doc2 = dict(guid='2', datetime='2012-11-29 12:13', site='a')
    >>> get_key(doc1) != get_key(doc2)
    True

    """
    # date might be 'YYYY-mm-dd HH:MM'
    date = doc['datetime'].partition(' ')[0]
    try:
        yy, mm, dd = date.split('-')
    except ValueError:
        raise ValueError("Could not parse date from {!r}".format(date))
    kwargs = {
        'year': yy,
        'month': mm,
        'day': dd,
        'guid': doc['guid'],
        'site': doc['site'],
    }
    return KEY_FORMAT.format(**kwargs)


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
