from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_selection import (
    SelectPercentile, chi2,
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline, FeatureUnion

from yatiri import tokenize
from yatiri.features import TfidfVectorizer, get_preprocessor
from yatiri.stemming import get_stemmer
from yatiri.stopwords import STOP_WORDS


class DenseMatrixTransformer(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X.todense()



def get_tokenizer():
    stem = get_stemmer().stem
    def tokenizer(text):
        tokens = []
        for token in tokenize.only_ascii_words(text.lower()):
            if token not in STOP_WORDS:
                tokens.append(token)
        return tokens
    return tokenizer


def default_vectorizer(**defaults):
    defaults.setdefault('analyzer', 'word')
    defaults.setdefault('tokenizer', get_tokenizer())
    defaults.setdefault('strip_accents', None)
    return TfidfVectorizer(**defaults)


def default_classifier(**defaults):
    defaults.setdefault('alpha', .0001)
    defaults.setdefault('n_iter', 50)
    defaults.setdefault('penalty', 'elasticnet')
    return SGDClassifier(**defaults)


def default_select(**defaults):
    defaults.setdefault('score_func', chi2)
    defaults.setdefault('percentile', 16)
    return SelectPercentile(**defaults)


def build_model_a():
    title = default_vectorizer()
    return Pipeline([
        ('vect', default_vectorizer()),
        ('clf', default_classifier()),
    ])


def build_model_b():
    return Pipeline([
        ('vect', default_vectorizer()),
        ('select', default_select()),
        ('clf', default_classifier()),
    ])


def build_model_c():

    title = default_vectorizer(preprocessor=get_preprocessor('headline'))
    body = default_vectorizer()

    ft = FeatureUnion([
            ('title', title),
            ('body', body),
        ],
        transformer_weights={
            'title': 1.2,
            'body': 1,
        })

    return Pipeline([
        ('vect', ft),
        ('select', default_select()),
        ('clf', default_classifier()),
    ])


def build_model_d():
    clf = RandomForestClassifier(
        max_depth=5,
        n_estimators=10,
        max_features='auto',
        random_state=42,
    )

    return Pipeline([
        ('vect', default_vectorizer()),
        ('todense', DenseMatrixTransformer()),
        ('clf', clf),
    ])


