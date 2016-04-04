#encoding: utf8

from contextlib import contextmanager

@contextmanager
def signal_context(signal, sender):
    recorded = []
    def record(sender, **kwargs):
        recorded.append(kwargs)
    signal.connect(record, sender)
    try:
        yield recorded
    finally:
        signal.disconnect(record, sender)