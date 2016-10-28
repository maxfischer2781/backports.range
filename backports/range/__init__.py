"""The range class from Python3"""
from __future__ import print_function, division
import operator
import itertools


try:
    # noinspection PyCompatibility
    import __builtin__
except ImportError:
    # noinspection PyCompatibility
    import builtins as __builtin__
#: original range builtin
builtin_range = __builtin__.range
try:  # Py2
    builtin_xrange = __builtin__.xrange
except AttributeError:  # Py3
    builtin_xrange = __builtin__.range

try:
    from itertools import zip_longest as izip_longest
except ImportError:
    from itertools import izip_longest


# noinspection PyShadowingBuiltins,PyPep8Naming
class range(object):
    def __init__(self, start_stop, stop=None, step=None):
        """
        The arguments to the range constructor must be integers (either built-in
        :class:`int` or any object that implements the ``__index__`` special
        method).  If the *_step* argument is omitted, it defaults to ``1``.
        If the *_start* argument is omitted, it defaults to ``0``.
        If *_step* is zero, :exc:`ValueError` is raised.

        For a positive *_step*, the contents of a range ``r`` are determined by the
        formula ``r[i] = _start + _step*i`` where ``i >= 0`` and
        ``r[i] < _stop``.

        For a negative *_step*, the contents of the range are still determined by
        the formula ``r[i] = _start + _step*i``, but the constraints are ``i >= 0``
        and ``r[i] > _stop``.

        A range object will be empty if ``r[0]`` does not meet the value
        constraint. Ranges do support negative indices, but these are interpreted
        as indexing from the end of the sequence determined by the positive
        indices.
        """
        # docstring taken from https://docs.python.org/3/library/stdtypes.html
        if stop is None:
            self._start = 0
            self._stop = operator.index(start_stop)
            self._step = 1
        else:
            self._start = operator.index(start_stop)
            self._stop = operator.index(stop)
            self._step = operator.index(step) if step is not None else 1
        if self._step == 0:
            raise ValueError('range() arg 3 must not be zero')

    # attributes are read-only
    @property
    def start(self):
        return self._start

    @property
    def stop(self):
        return self._stop

    @property
    def step(self):
        return self._step

    def __bool__(self):
        if self._step > 0:
            return self._start < self._stop
        return self._start > self._stop

    __nonzero__ = __bool__

    # NOTE:
    # We're repeatedly calling self.__len__() instead of len(self)!
    # The len-protocol can cause overflow, since it only expects an int, not
    # py2 long int etc. We circumvent this with the direct call.
    def __len__(self):
        _len = (self._stop - self._start) // self._step
        _len += 1 if (self._stop - self._start) % self._step else 0
        return _len if _len > 0 else 0

    def __getitem__(self, item):
        # index) range(1, 10, 2)[3] => 1 + 2 * 3 if < 10
        # slice) range(1, 10, 2)[1:3] => range(3, 7)
        # There are no custom slices allowed, so we can do a fast check
        # see: http://stackoverflow.com/q/39971030/5349916
        if item.__class__ is slice:
            # we cannot use item.indices since that may overflow...
            start, stop, stride, max_len = item.start, item.stop, item.step, self.__len__()
            start = 0 if start is None else operator.index(start)
            start = min(max_len + start if start < 0 else start, max_len)
            stop = max_len if stop is None else operator.index(stop)
            stop = min(max_len + stop if stop < 0 else stop, max_len)
            stride = 1 if stride is None else stride
            if start == stop:
                return self.__class__(0, 0)
            return self.__class__(self[start], self[stop], self.step * stride)
        if item < 0:
            item += self.__len__()
        if item >= self.__len__() or item < 0:
            raise IndexError('range object index out of range %s' % item)
        return self._start + self._step * item

    def __iter__(self):
        # Let's reinvent the wheel again...
        # We *COULD* use xrange here, but that leads to OverflowErrors etc.
        idx, max_len = 0, self.__len__()
        #print(self, max_len)
        #print('iter', end='<')
        while idx < max_len:
            yield self[idx]
            #print(self[idx], end=',')
            idx += 1
        #print('>')

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return (
                # empty range
                (not self and not other)
                # same values
                or self.__len__() == other.__len__()
                and (
                    (
                        # if there is only one element, only the first
                        # aka start counts
                        self.__len__() == 1
                        and self._start == other.start
                    ) or (
                        # first value must match
                        self._start == other.start
                        # distance between values must match
                        and self._step == other.step
                        # Do not test final element - we've got the same number of
                        # elements, at same distance, from same start, giving the
                        # same end sequence.
                    )
                )
            )
        return NotImplemented
        # do some trivial checks
        if isinstance(other, (list, tuple)):
            if len(other) != self.__len__():
                return False
        return all(my_val == other_val for my_val, other_val in izip_longest(self, other))

    def __ne__(self, other):
        return not self == other

    # order comparisons are forbidden
    def __lt__(self, other):
        return NotImplemented
        #raise TypeError('unorderable types: range() < range()')



    def __contains__(self, item):
        trivial_test_val = self._trivial_test_type(item)
        if trivial_test_val is not None:
            return self._contains_int(trivial_test_val)
        # take the slow path, compare every single item
        return any(self_item == item for self_item in self)

    @staticmethod
    def _trivial_test_type(value):
        try:
            # we can contain only int-like objects
            val = int(value)
            if val != value:
                raise TypeError
        except (TypeError, ValueError, AttributeError):
            # however, an object may compare equal to our items
            return None
        else:
            return val

    def _contains_int(self, integer):
        if self._step == 1:
            return self._start <= integer < self._stop
        elif self._step > 0:
            return self._stop > integer >= self._start and integer % self._step == self._start % self._step
        elif self._step < 0:
            return self._stop < integer <= self._start and integer % self._step == self._start % self._step

    def index(self, value):
        trivial_test_val = self._trivial_test_type(value)
        if trivial_test_val is not None:
            if self._contains_int(trivial_test_val):
                return (value - self._start) // self._step
        else:
            # take the slow path, compare every single item
            for idx, self_item in enumerate(self):
                if self_item == value:
                    return idx
        raise ValueError('%r is not in range' % value)

    def count(self, value):
        trivial_test_val = self._trivial_test_type(value)
        if trivial_test_val is not None:
            return 1 if self._contains_int(trivial_test_val) else 0
        # take the slow path, compare every single item
        _count = 0
        for idx, self_item in enumerate(self):
            if self_item == value:
                _count += 1
        return _count

    def __hash__(self):
        # Hash should signify the same sequence of values
        # We hash a tuple of values that define the range.
        # derived from rangeobject.c
        my_len = self.__len__()
        if not my_len:
            return hash((0, None, None))
        elif my_len == 1:
            return hash((my_len, self._start, None))
        return hash((my_len, self._start, self._step))

    def __repr__(self):
        if self.step != 1:
            return '%s(%s, %s, %s)' % (self.__class__.__name__, self._start, self._stop, self._step)
        return '%s(%s, %s)' % (self.__class__.__name__, self._start, self._stop)
