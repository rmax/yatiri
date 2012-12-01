import re

RE_ONLY_WORDS = re.compile(r'\b[a-z]\w+\b', re.I|re.U)


def only_ascii_words(text):
    """Returns ascii words without numbers.

    >>> only_ascii__words('foo bar, 123 aj 4a.')
    ['foo', 'bar', 'aj']
    """
    return RE_ONLY_WORDS.findall(text)
