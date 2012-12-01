
KEY_FORMAT = 'news:{year}{month}{day}:{site}:{guid}'


def next_key(key):
    """Returns following key value. Suitable for range scan of prefixes.

    >>> next_key('root:prefix:')
    'root:prefix;'

    """
    return key[:-1] + chr(ord(key[-1])+1)


def get_key(doc):
    """Returns unique key for given document.

    >>> doc1 = dict(guid='1', datetime='2012-11-29', site='a')
    >>> doc2 = dict(guid='2', datetime='2012-11-29 12:13', site='a')
    >>> get_key(doc1) != get_key(doc2)
    True

    """
    # date might be 'YYYY-mm-dd HH:MM'
    date = doc['datetime'].partition(' ')[0]
    try:
        yy, mm, dd = date.split('-')
    except ValueError:
        raise ValueError("Could not parse date from {!r}".format(date))
    kwargs = {
        'year': yy,
        'month': mm,
        'day': dd,
        'guid': doc['guid'],
        'site': doc['site'],
    }
    return KEY_FORMAT.format(**kwargs)


