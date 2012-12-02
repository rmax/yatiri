
from cyclone import web
from txrho.xapian import SearchPool
from twisted.internet import reactor, defer

from yatiri import settings
from yatiri.batch.search import query as execute_query
from yatiri.web import BaseHandler as _BaseHandler


SETTINGS_MAP = (
    ('debug', 'DEBUG'),
)


class BaseHandler(_BaseHandler):

    @property
    def searchpool(self):
        return self.settings['searchpool']

    def run(self, *args, **kwargs):
        return self.searchpool.runWithConnection(*args, **kwargs)

    def success(self, data):
        data.setdefault('ok', True)
        self.finish(data)

    def error(self, reason):
        self.finish({'error': True, 'reason': reason})


class IndexHandler(BaseHandler):

    @web.asynchronous
    def get(self):
        return self.run(self._on_conn)

    def _on_conn(self, conn):
        self.success({
            'documents': conn.get_doccount(),
        })



class SearchHandler(BaseHandler):

    @web.asynchronous
    def get(self):
        q = self.get_arg('q', '')

        try:
            offset = int(self.get_arg('offset', 0))
        except ValueError:
            return self.error('invalid_offset')

        if offset < 0:
            return self.error('invalid_offset')

        try:
            limit = int(self.get_arg('limit', 10))
        except ValueError:
            return self.error('invalid_limit')

        if limit < 0:
            return self.error('invalid_limit')

        return self.run(self._query, q, offset, limit)

    def _query(self, sconn, q, offset, limit):
        if q:
            q = sconn.query_parse(q)
        else:
            q = sconn.query_all()
        categories = self.get_args('category')
        if categories:
            qc = sconn.query_composite(
                sconn.OP_OR, [
                    sconn.query_field('category', value)
                    for value in categories
                ])
            q = sconn.query_composite(
                sconn.OP_AND, [q, qc])
        self.log('Query: {!r}'.format(q))
        results = execute_query(sconn, q, offset, limit)
        self.success({
            'total': results.matches_estimated,
            'is_exact': results.estimate_is_exact,
            'docs': [
                dict(id=r.id, category=r.get_terms('category').next()) for r in results
            ]
        })


def get_app():
    handlers = [
        (r'/', IndexHandler),
        (r'/search', SearchHandler),
    ]
    app_settings = dict(
        (k, getattr(settings, v.upper())) for (k,v) in SETTINGS_MAP
    )
    # setup xapian
    searchpool = SearchPool(settings.XAPIAN_DB)
    reactor.callWhenRunning(searchpool.start)
    app_settings['searchpool'] = searchpool

    return web.Application(handlers, **app_settings)
