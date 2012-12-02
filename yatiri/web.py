from cyclone import web
import yatiri.datastore
import yatiri.settings


SETTINGS_MAP = (
    ('debug', 'DEBUG'),
    ('cookie_secret', 'COOKIE_SECRET'),
    ('login_url', 'LOGIN_URL'),
    ('logout_url', 'LOGOUT_URL'),
    ('static_path', 'STATIC_PATH'),
    ('templates_path', 'TEMPLATES_PATH'),
)


class IndexHandler(web.RequestHandler):

    def get(self):
        self.write("hello world")


def get_app():
    handlers = [
        (r'/', IndexHandler),
    ]
    params = dict(
        (k, getattr(yatiri.settings, v.upper())) for (k,v) in SETTINGS_MAP
    )
    # setup leveldb
    params['levelpool'] = yatiri.datastore.pool

    return web.Application(handlers, **params)
