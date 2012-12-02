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

CATEGORY_MAP = {
    'inestabilidad': 'politica',
    'inseguridad': 'seguridad',
    'conflictos': 'conflictos',
}


class BaseHandler(web.RequestHandler):

    def get_args(self, name, default=None):
        return self.request.arguments.get(name, default)

    def get_arg(self, name, default=None):
        return self.get_args(name, [default])[0]

    def log(self, msg):
        log.msg(msg, system=self.__class__.__name__)

    def logerr(self, msg):
        log.err(msg, system=self.__class__.__name__)


    def render(self, template_name, **kwargs):
        kwargs.setdefault('summary', doc_summary)
        return super(BaseHandler, self).render(template_name, **kwargs)

    def render_error(self, **kwargs):
        return self.render('error.html', **kwargs)



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
    def fetch_docs(self, query, categories=()):
        try:
            data = yield self.client.search(query, categories)
        except Exception as e:
            self.logerr('error while retrieveing results for {!r}'.format(query))
            self.render_error()
            defer.returnValue(None)

        if 'error' in data:
            self.logerr('error from search search: {!r}'.format(data))
            self.render_error()
            defer.returnValue(None)

        results = []
        for ret in data['docs']:
            info = self.corpus_db.get(ret['id'])
            if not info:
                self.log('document key without record {!r}'.format(ret))
                continue
            if any(f not in info for f in ('headline', 'body', 'url')):
                self.log("Document with missing fields: {!r}".format(info))
                break
            doc = ObjectDict((k,v) for (k,v) in ret.items()
                             if not k.startswith('_'))
            doc.update(info)
            results.append(doc)

        defer.returnValue(results)


    @defer.inlineCallbacks
    def get(self):
        q = self.get_arg('q')
        categories = self.get_args('category')
        if categories:
            categories = [CATEGORY_MAP[c] for c in categories]
        else:
            categories = CATEGORY_MAP.keys()
        if q:
            results = yield self.fetch_docs(q, categories)
            kwargs = dict(
                query=q,
                results=results,
            )
            if results:
                self.render("search_results.html", **kwargs)
            else:
                self.render("search_noresults.html", **kwargs)

        else:
            self.redirect("/")


class CategoryHandler(SearchHandler):

    @defer.inlineCallbacks
    def get(self, category):
        category = CATEGORY_MAP[category]
        self.log(category)
        results = yield self.fetch_docs('', [category])
        if results:
            kwargs = dict(
                results=results,
            )
            self.render("category_list.html", **kwargs)


def get_app():
    handlers = [
        (r'/', IndexHandler),
        (r'/search/?', SearchHandler),
        (r'/({})/?'.format(r'|'.join(CATEGORY_MAP.keys())), CategoryHandler),
    ]
    app_settings = dict(
        (k, getattr(settings, v.upper())) for (k,v) in SETTINGS_MAP
    )
    # leveldb
    app_settings['levelpool'] = datastore.pool
    # search
    app_settings['searchclient'] = SearchClient(settings.SEARCH_ENDPOINT)

    return web.Application(handlers, **app_settings)
