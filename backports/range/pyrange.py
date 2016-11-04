"""The range class from Python3"""
from __future__ import division
import operator
import platform

try:
    import collections.abc as _abc
except ImportError:
    import collections as _abc

try:
    from itertools import zip_longest as izip_longest
except ImportError:
    from itertools import izip_longest

# default integer __eq__
# python 2 has THREE separate integer type comparisons we need to check
try:
    _int__eq__s = set((int.__eq__, long.__eq__, bool.__eq__))
except NameError:
    _int__eq__s = set((int.__eq__,))

# check whether this file is being compiled and must follow Cython standards
try:
    import cython as _cython
    if not _cython.compiled:  # pragma: no cover
        raise ImportError
except ImportError:
    CYTHON_COMPILED = False  # noqa
else:  # coverage: cython compiled only
    CYTHON_COMPILED = True  # noqa

# need iterator in separate file to avoid import loop
# cython iterator uses python iterator for pickling
from .pyrange_iterator import range_iterator


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

    def __nonzero__(self):
        return self._bool

    __bool__ = __nonzero__

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
        return range_iter(self._start, self.step, self._len)

    def __reversed__(self):
        # this is __iter__ in reverse, *by definition*
        if self._len:
            return range_iter(self[-1], -self.step, self._len)
        else:
            return range_iter(0, 1, 0)

    # Comparison Methods
    # Cython requires the use of __richcmp__ *only* and fails
    # when __eq__ etc. are present.
    # Each __OP__ is defined as __py_OP__ and rebound as required.
    def __py_eq__(self, other):
        if isinstance(self, other.__class__):
            if self is other:
                return True
            # unequal number of elements
            # check this first to imply some more features
            # NOTE: call other._len to avoid OverFlow
            elif self._len != other._len:
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

    def __py_ne__(self, other):
        return not self == other

    # order comparisons are forbidden
    def __py_ord__(self, other):
        """__gt__ = __le__ = __ge__ = __lt__ = __py_ord__"""
        return NotImplemented

    def __richcmp__(self, other, comp_opcode):  # pragma: no cover
        # Cython:
        # Do not rely on the first parameter of these methods, being "self" or the right type.
        # The types of both operands should be tested before deciding what to do.
        if not isinstance(self, range):
            # if other is not of type(self), we can't compare it anyways
            return NotImplemented
        # Comparison opcodes:
        # < <= == != > >=
        # 0  1  2  3 4  5
        if comp_opcode == 2:
            return self.__py_eq__(other)
        elif comp_opcode == 3:
            return not self.__py_eq__(other)
        else:
            return NotImplemented

    if not CYTHON_COMPILED:
        __eq__ = __py_eq__
        __ne__ = __py_ne__
        __gt__ = __le__ = __ge__ = __lt__ = __py_ord__

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
        trivial_test_val = range._trivial_test_type(value)
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
        trivial_test_val = range._trivial_test_type(value)
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

try:
    # see if we have the Cython compiled long-long-iterator
    # ALWAYS use pure-python for incompatible implementations
    if platform.python_implementation() != 'CPython':
        raise ImportError
    from .cyrange_iterator import llrange_iterator
except ImportError:
    # if not, expose the python iterator directly
    range_iter = range_iterator
else:
    # if yes, create a factory to pick the best one
    def range_iter(start, step, count):
        # C long long must support inclusive range [-9223372036854775807, +9223372036854775807]
        if (
                -9223372036854775807 <= start <= 9223372036854775807
                and -9223372036854775807 <= step <= 9223372036854775807
                and -9223372036854775807 <= count <= 9223372036854775807
                and -9223372036854775807 <= start + step * count <= 9223372036854775807
        ):
            try:
                return llrange_iterator(start, step, count)
            except OverflowError:
                print(start, step, count)
                raise
        return range_iterator(start, step, count)

# register at ABCs
# do not use decorators to play nice with Cython
_abc.Sequence.register(range)
_abc.Iterator.register(range_iterator)
