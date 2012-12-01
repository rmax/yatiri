import hashlib
import logging
import re

logger = logging.getLogger(__name__)

RE_SITE_ID = {
    'eldia': re.compile(r'[\?&]id_articulo=(\d+)'),
    'eldeber': re.compile(r'[\?&]id=(\d+)'),
    'opinion': re.compile(r'[\?&]id=(\d+)'),
    'lostiempos': re.compile(r'_(\d+)_(\d+)\.html'),
    'eldiario': re.compile(r'/(nt\d{6})/.+?[\?&]n=(\d+)'),
    'laprensa': re.compile(r'_(\d+)_(\d+)\.html'),
}


def doc_guid(doc):
    """Returns unique hash per document.

    >>> doc1 = {'url': 'url1'}
    >>> doc2 = {'url': 'url2'}
    >>> doc_guid(doc1) == doc_guid(doc1)
    True
    >>> doc_guid(doc1) == doc_guid(doc2)
    False

    """
    h = hashlib.sha1()
    url = doc['url'].encode('utf-8')
    site = doc.get('site')
    if site and site in RE_SITE_ID:
        match = RE_SITE_ID[site].search(url)
        if match:
            h.update(site)
            for value in RE_SITE_ID[site].search(url).groups():
                h.update(value)
        else:
            logger.warning(
                "Site id matching failed: {} -- {}".format(site, url))
            h.update(url)
    else:
        h.update(url)
    return h.hexdigest()
