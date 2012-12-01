from nltk.corpus import stopwords as nltk_stopwords
from sklearn.feature_extraction.text import strip_accents_ascii


# normalized stopwords
STOP_WORDS = map(lambda s: s.decode('utf-8'), nltk_stopwords.words('spanish'))
STOP_WORDS = map(strip_accents_ascii, STOP_WORDS)
STOP_WORDS += [
]
