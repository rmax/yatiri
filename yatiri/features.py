from sklearn.base import BaseEstimator
from sklearn.feature_extraction.text import (
    TfidfVectorizer, strip_accents_ascii,
)
from sklearn.pipeline import FeatureUnion
from sklearn.preprocessing import MinMaxScaler


def remove_non_ascii(s):
    return "".join(i for i in s if ord(i) < 128)


class DocumentVectorizer(BaseEstimator):

    def fit(self, raw_docs, y=None):
        self.fit_transform(raw_docs, y)
        return self

    def fit_transform(self, raw_docs, y=None):
        headlines, body = self._preprocess(raw_docs)

