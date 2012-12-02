from os.path import join, dirname


DEBUG = True

PROJECT_ROOT = dirname(dirname(__file__))

LEVELDB_ROOT = join(PROJECT_ROOT, 'databases')
XAPIAN_DB = join(PROJECT_ROOT, 'xapiandb')

# web settings
STATIC_PATH = join(PROJECT_ROOT, 'static')
TEMPLATE_PATH = join(PROJECT_ROOT, 'templates')
COOKIE_SECRET = '32oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo='
LOGIN_URL = '/login'
LOGOUT_URL = '/logout'
SEARCH_ENDPOINT = 'http://localhost:9999/'

# search settings


try:
    from settings_local import *
except ImportError:
    pass
