import msgpack
from leveldict import LevelDictEncoded, LevelPool

from yatiri import settings


class MessagePackEncoder(object):
    """MsgPack encode/decode interface"""
    def __init__(self):
        self.encode = msgpack.dumps
        self.decode = msgpack.loads


# single instance
pool = LevelPool(
    settings.LEVELDB_ROOT,
    leveldb_cls=LevelDictEncoded,
    encoder=MessagePackEncoder(),

)

def corpus_db():
    return pool['corpus']

def training_db():
    return pool['training']

def staging_db():
    return pool['staging']

def prod_db():
    return pool['prod']
