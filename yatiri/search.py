
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
        self.finish({'error': reason})


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
        q = self.get_arg('q')
        if not q:
            return self.error('empty_query')

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
        results = execute_query(sconn, q, offset, limit)
        self.success({
            'total': results.matches_estimated,
            'is_exact': results.estimate_is_exact,
            'docs': [
                {'id': r.id} for r in results
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
