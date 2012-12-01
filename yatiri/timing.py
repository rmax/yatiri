import time


class Timer(object):

    def __init__(self):
        self.reset()

    def reset(self):
        self.started = 0
        self.finished = 0

    def start(self):
        assert not self.started, "already started"
        self.started = time.time()

    def stop(self):
        assert self.started, "not started"
        assert not self.finished, "already finished"
        self.finished = time.time()

    @property
    def elapsed(self):
        assert self.started, "not started"
        if self.finished:
            return self.finished - self.started
        return time.time() - self.started

    # context protocol
    def __enter__(self):
        self.start()

    def __exit__(self, *args):
        self.stop()


class RuntimeCallback(object):

    def __init__(self, callback):
        self.timer = Timer()
        self.callback= callback

    def __enter__(self):
        self.timer.start()

    def __exit__(self, *args):
        if not args[0]:
            self.callback(self.timer)


def LogRuntime(msg, logger=None, loglevel='debug'):
    if not logger:
        import logging
        logger = logging.getLogger()
    logmsg = getattr(logger, loglevel.lower())
    return RuntimeCallback(lambda t: logmsg(msg.format(t, timer=t,
                                                       elapsed=t.elapsed)))


