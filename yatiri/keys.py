

def next_key(key):
    """Returns following key value. Suitable for range scan of prefixes.

    >>> next_key('root:prefix:')
    'root:prefix;'

    """
    return key[:-1] + chr(ord(key[-1])+1)
