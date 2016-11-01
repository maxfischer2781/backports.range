"""The range class from Python3"""
from __future__ import division
import operator
import sys

try:
    import collections.abc as _abc
except ImportError:
    import collections as _abc

try:
    from itertools import zip_longest as izip_longest
except ImportError:
    from itertools import izip_longest

# default integer __eq__
# python 2 has TWO separate integer types we need to check
try:
    _int__eq__s = set((int.__eq__, long.__eq__))
except NameError:
    _int__eq__s = set((int.__eq__,))


# noinspection PyShadowingBuiltins,PyPep8Naming
class range(object):
    __slots__ = ('_start', '_stop', '_step', '_len', '_bool')

    def __init__(self, start_stop, stop=None, step=None):
        """
        Object that produces a sequence of integers from start (inclusive) to
        stop (exclusive) by step.

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
        # length depends only on read-only values, so compute it only once
        # practically ALL methods use it, so compute it NOW
        # range is required to handle large ints outside of float precision
        _len = (self._stop - self._start) // self._step
        _len += 1 if (self._stop - self._start) % self._step else 0
        self._len = 0 if _len < 0 else _len
        self._bool = bool(self._len)

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
        return self._bool

    __nonzero__ = __bool__

    # NOTE:
    # We repeatedly use self._len instead of len(self)!
    # The len-protocol can cause overflow, since it only expects an int, not
    # py2 long int etc. We circumvent this with the direct lookup.
    def __len__(self):
        return self._len

    def __getitem__(self, item):
        # index) range(1, 10, 2)[3] => 1 + 2 * 3 if < 10
        # slice) range(1, 10, 2)[1:3] => range(3, 7)
        # There are no custom slices allowed, so we can do a fast check
        # see: http://stackoverflow.com/q/39971030/5349916
        if item.__class__ is slice:
            # we cannot use item.indices since that may overflow in py2.X...
            start, stop, stride, max_len = item.start, item.stop, item.step, self._len
            # nothing to slice on
            if not max_len:
                return self.__class__(0, 0)
            if start is None:  # unset, use self[0]
                new_start = self._start
            else:
                start_idx = operator.index(start)
                if start_idx >= max_len:  # cut off out-of-range
                    new_start = self._stop
                elif start_idx < -max_len:
                    new_start = self._start
                else:
                    new_start = self[start_idx]
            if stop is None:
                new_stop = self._stop
            else:
                stop_idx = operator.index(stop)
                if stop_idx >= max_len:
                    new_stop = self._stop
                elif stop_idx < -max_len:
                    new_stop = self._start
                else:
                    new_stop = self[stop_idx]
            stride = 1 if stride is None else stride
            return self.__class__(new_start, new_stop, self.step * stride)
        # check type first
        val = operator.index(item)
        if val < 0:
            val += self._len
        if val < 0 or val >= self._len:
            raise IndexError('range object index out of range')
        return self._start + self._step * val

    def __iter__(self):
        # Let's reinvent the wheel again...
        # We *COULD* use xrange here, but that leads to OverflowErrors etc.
        return range_iterator(self._start, self.step, self._len)

    def __reversed__(self):
        # this is __iter__ in reverse, *by definition*
        if self._len:
            return range_iterator(self[-1], -self.step, self._len)
        else:
            return range_iterator(0, 1, 0)

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            if self is other:
                return True
            # unequal number of elements
            # check this first to imply other features
            # NOTE: call other.__len__ to avoid OverFlow
            elif self._len != other.__len__():
                return False
            # empty sequences
            elif not self:
                return True
            # first element must match
            elif self._start != other.start:
                return False
            # just that one element
            elif self._len == 1:
                return True
            # final element is implied by same start, count and step
            else:
                return self._step == other.step
        # specs assert that range objects may ONLY equal to range objects
        return NotImplemented

    def __ne__(self, other):
        return not self == other

    # order comparisons are forbidden
    def __lt__(self, other):
        return NotImplemented

    __gt__ = __le__ = __ge__ = __lt__

    def __contains__(self, item):
        # specs use fast comparison ONLY for pure ints
        # subtypes are not allowed, so that custom __eq__ can be used
        # we use fast comparison only if:
        #   a type does use the default __eq__
        try:
            if type(item).__eq__ not in _int__eq__s:
                raise AttributeError
        except AttributeError:
            # take the slow path, compare every single item
            return any(self_item == item for self_item in self)
        else:
            return self._contains_int(item)

    @staticmethod
    def _trivial_test_type(value):
        try:
            # we can contain only int-like objects
            val = operator.index(value)
        except (TypeError, ValueError, AttributeError):
            # however, an object may compare equal to our items
            return None
        else:
            return val

    def _contains_int(self, integer):
        # NOTE: integer is not a C int but a Py long
        if self._step == 1:
            return self._start <= integer < self._stop
        elif self._step > 0:
            return self._stop > integer >= self._start and not (integer - self._start) % self._step
        elif self._step < 0:
            return self._stop < integer <= self._start and not (integer - self._start) % self._step

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
        my_len = self._len
        if not my_len:
            return hash((0, None, None))
        elif my_len == 1:
            return hash((1, self._start, None))
        return hash((my_len, self._start, self._step))

    def __repr__(self):
        if self.step != 1:
            return '%s(%s, %s, %s)' % (self.__class__.__name__, self._start, self._stop, self._step)
        return '%s(%s, %s)' % (self.__class__.__name__, self._start, self._stop)

    # Pickling
    def __getstate__(self):
        return self._start, self._stop, self._step, self._len

    def __setstate__(self, state):
        self._start, self._stop, self._step, self._len = state
        self._bool = bool(self._len)


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

# register at ABCs
# do not use decorators to play nice with Cython
_abc.Sequence.register(range)
_abc.Iterator.register(range_iterator)