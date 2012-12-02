import xappy
from xappy import FieldActions

from yatiri import settings


MAX_MEM = 512 * 1024 * 1024 # in bytes

TEXT_DEFAULTS = {
    'language': 'es',
    'nopos': True,
}

TEXT_FIELDS = (
    'headline',
    'teaser',
    'body',
)

TEXT_WEIGHTS = {
    'headline': 3,
    'teaser': 2,
    'body': 1,
}

EXACT_FIELDS = {
    'type',
}


class IndexerContext(object):
    def __init__(self, dbpath):
        self.dbpath = dbpath

    def __enter__(self):
        self.conn = xappy.IndexerConnection(self.dbpath)
        self.conn.set_max_mem_use(MAX_MEM)
        return self.conn

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.conn.close()
        self.conn = None


def create_index(conn):
    for name in TEXT_FIELDS:
        kwargs = TEXT_DEFAULTS.copy()
        kwargs.update({
            'weight': TEXT_WEIGHTS[name],
        })
        conn.add_field_action(name, FieldActions.INDEX_FREETEXT, **kwargs)

    for name in EXACT_FIELDS:
        conn.add_field_action(name, FieldActions.INDEX_EXACT)


def index(items, doc_type, create=False):
    indexer = IndexerContext(settings.XAPIAN_DB)
    if create:
        with indexer as conn:
            create_index(conn)

    with indexer as conn:
        n = 0
        for n, (key, data) in enumerate(items, 1):
            doc = xappy.UnprocessedDocument(key)
            doc.append('type', doc_type)
            for field in TEXT_FIELDS:
                doc.append(field, data.get(field, ''))
            conn.add(doc)
        return n


def query(sconn, search, offset, limit):
    q = sconn.query_parse(search, default_op=sconn.OP_AND)
    return sconn.search(q, startrank=offset, endrank=offset+limit)
