from cyclone import web
from cyclone.util import ObjectDict
from twisted.internet import defer
from twisted.python import log

from yatiri import datastore, settings
from yatiri.searchclient import SearchClient
from yatiri.utils import doc_summary


SETTINGS_MAP = (
    ('debug', 'DEBUG'),
    ('cookie_secret', 'COOKIE_SECRET'),
    ('login_url', 'LOGIN_URL'),
    ('logout_url', 'LOGOUT_URL'),
    ('static_path', 'STATIC_PATH'),
    ('template_path', 'TEMPLATE_PATH'),
)


class BaseHandler(web.RequestHandler):

    def get_args(self, name, default=None):
        return self.request.arguments.get(name, default)

    def get_arg(self, name, default=None):
        return self.get_args(name, [default])[0]

    def log(self, msg, level='DEBUG'):
        log.msg(msg, system=self, level=level)


class IndexHandler(BaseHandler):

    def get(self):
        self.render('index.html')


class SearchHandler(BaseHandler):

    @property
    def client(self):
        return self.settings['searchclient']

    @property
    def corpus_db(self):
        return self.settings['levelpool']['corpus']

    @defer.inlineCallbacks
    def get(self):
        q = self.get_arg('q')
        if q:
            try:
                data = yield self.client.search(q)
            except Exception:
                self.log('error while retrieveing results for {!r}'.format(q),
                         level='ERROR')
                self.finish("error while retrieving search results")
                defer.returnValue(None)

            if 'error' in data:
                self.log('error from search search: {!r}'.format(data))
                self.finish("error: {}".format(data['reason']))
                defer.returnValue(None)

            results = []
            for ret in data['docs']:
                info = self.corpus_db.get(ret['id'])
                if not info:
                    self.log('document key without record {!r}'.format(ret))
                    continue
                doc = ObjectDict(id=ret['id'])
                doc.update(info)
                results.append(doc)

            kwargs = dict(
                query=q,
                results=results,
                summary=doc_summary,
            )
            if results:
                self.render("search_results.html", **kwargs)
            else:
                self.render("search_noresults.html", **kwargs)

        else:
            self.redirect("/")


def get_app():
    handlers = [
        (r'/', IndexHandler),
        (r'/search', SearchHandler),
    ]
    app_settings = dict(
        (k, getattr(settings, v.upper())) for (k,v) in SETTINGS_MAP
    )
    # leveldb
    app_settings['levelpool'] = datastore.pool
    # search
    app_settings['searchclient'] = SearchClient(settings.SEARCH_ENDPOINT)

    return web.Application(handlers, **app_settings)
