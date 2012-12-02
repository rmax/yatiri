import json

from urllib import urlencode
from urlparse import urljoin
from twisted.internet import defer
from cyclone import httpclient


class SearchClient(object):

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def fetch(self, url, *args, **kwargs):
        return httpclient.fetch(url, *args, **kwargs)

    @defer.inlineCallbacks
    def search(self, query, categories=(),  **kwargs):
        kwargs.update({
            'q': query,
            'category': categories,
        })
        url = urljoin(self.endpoint, '/search?{}'.format(
            urlencode(kwargs, doseq=1)))
        result = yield self.fetch(url)
        data = json.loads(result.body)
        defer.returnValue(data)



