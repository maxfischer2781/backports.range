import sys


class range_iterator(object):
    __slots__ = ('_start', '_stop', '_step', '_current')

    def __init__(self, start, step, count):
        """Iterator over a `range`, for internal use only"""
        self._start = start
        self._step = step
        self._stop = count - 1
        self._current = -1

    def __iter__(self):
        return self

    def _next(self):
        if self._current == self._stop:
            raise StopIteration
        self._current += 1
        return self._start + self._step * self._current

    if sys.version_info < (3,):
        next = _next
    else:
        __next__ = _next

    def __length_hint__(self):
        # both stop and current are offset by 1 which cancels out here
        return self._stop - self._current

    # Pickling
    def __getstate__(self):
        return self._start, self._stop, self._step, self._current

    def __setstate__(self, state):
        self._start, self._stop, self._step, self._current = state
