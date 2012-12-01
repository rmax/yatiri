import functools

from sklearn.feature_extraction.text import (
    TfidfVectorizer as _TfidfVectorizer
)

from yatiri.text import normalize_text
from yatiri.stopwords import STOP_WORDS


DEFAULT_FIELDS = (
    'headline',
    'subheadline',
    'teaser',
    'body',
)


def preprocessor(doc, fields):
    return normalize_text('\n'.join(
        doc.get(f, '') for f in fields
    ))


def get_preprocessor(*fields):
    if not fields:
        fields = DEFAULT_FIELDS
    return functools.partial(preprocessor, fields=fields)


class TfidfVectorizer(_TfidfVectorizer):
    stopwords = STOP_WORDS
    sublinear_tf = True

    def build_preprocessor(self):
        if self.preprocessor:
            return self.preprocessor
        return get_preprocessor()
