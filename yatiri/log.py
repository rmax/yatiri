import logging


def setup_logging(filename=None, level='DEBUG'):
    kwargs = {
        'datefmt': '%Y-%m-%d %H:%M:%S %Z',
        'format': '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        'level': level,
        'filename': filename,
    }
    logging.basicConfig(**kwargs)
