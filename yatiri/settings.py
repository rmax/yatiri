from os.path import join, dirname


PROJECT_ROOT = dirname(dirname(__file__))

LEVELDB_ROOT = join(PROJECT_ROOT, 'databases')
XAPIAN_DB = join(PROJECT_ROOT, 'xapiandb')


try:
    from settings_local import *
except ImportError:
    pass
