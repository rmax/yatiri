import functools
import logging


def log_output(func=None, prefix='', logger=None):
    if not logger:
        logger = logging.getLogger()

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ret = func(*args, **kwargs)
            logger.debug('{}{} output: {!r}'.format(prefix, func.__name__, ret))
            return ret
        return wrapper

    if func:
        return decorator(func)
    else:
        return decorator

