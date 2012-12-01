from nltk.stem import SnowballStemmer
from yatiri.stopwords import STOP_WORDS


def get_stemmer():
    stemmer = SnowballStemmer('spanish')
    stemmer.stopwords = set(STOP_WORDS)
    return stemmer
