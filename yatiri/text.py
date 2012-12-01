from sklearn.feature_extraction.text import strip_accents_ascii


def remove_non_ascii(s):
        return "".join(i for i in s if ord(i) < 128)


def normalize_text(text):
    """Basic normalization without altering the semantic"""
    text = strip_accents_ascii(text)
    text = remove_non_ascii(text)
    return text


