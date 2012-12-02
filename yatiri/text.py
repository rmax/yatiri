from sklearn.feature_extraction.text import strip_accents_ascii


def remove_non_ascii(s):
        return "".join(i for i in s if ord(i) < 128)


def normalize_text(text):
    """Basic normalization without altering the semantic"""
    if isinstance(text, str):
        # strip_accents_ascii requires unicode test
        text = text.decode('utf-8')
    text = strip_accents_ascii(text)
    text = remove_non_ascii(text)
    return text


