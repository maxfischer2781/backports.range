from __future__ import print_function
import itertools
from backports.range import range as backport_range

# Backports of testing infrastructure
try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from itertools import zip_longest as izip_longest
except ImportError:
    from itertools import izip_longest


class CustomRangeTest(unittest.TestCase):
    """Custom unittests for additional/compatibility features"""
    @staticmethod
    def _normalize_index(index, length):
        """Normalize an index to [0, length)"""
        return index % length

    @unittest.skipUnless(type(range(1)) == range, "no builtin range class")
    @unittest.skipUnless(range(0, 27) == range(0, 27), "no equality defined for builtin range")
    def test_compare_builtin(self):
        """Compatibility: backport range equal to builtin range"""
        init_args = (
            # start only
            (15,), (128,), (-127,),
            # default step ranges
            (1, 2), (-50, 50, 1), (-256, -255),
            # C long long barrier
            (-9223372036854775809, -9223372036854775807), (9223372036854775807, 9223372036854775809),
            # empty ranges
            (1, 1, 1), (20, 0, 1), (0, 50, -1), (0, 0),
            # regular ranges
            (1, 120, 5), (1, 119, 5), (-27, 0, 2), (0, -27, 2)
        )
        for args_a, args_b in itertools.product(init_args, repeat=2):
            with self.subTest(init_a=args_a, init_b=args_b):
                # conform to builtin equality rules
                if range(*args_a) == range(*args_b):
                    self.assertEqual(backport_range(*args_a), backport_range(*args_b))
                    self.assertEqual(backport_range(*args_a), range(*args_b))
                    self.assertEqual(range(*args_a), backport_range(*args_b))
                else:
                    self.assertNotEqual(backport_range(*args_a), backport_range(*args_b))
                    self.assertNotEqual(backport_range(*args_a), range(*args_b))
                    self.assertNotEqual(range(*args_a), backport_range(*args_b))

    def test_index_start_stop(self):
        """Compatibility: range.index start and stop arguments (py3.5 collections.abc.Sequence)"""
        ranges = [
            backport_range(10), backport_range(5, 15), backport_range(0, -10, -1),
            backport_range(-9223372036854775810, -9223372036854775807)
        ]

        class Wrapper(object):
            def __init__(self, value):
                self.value = value

            def __eq__(self, other):
                return self.value == other

        class AlwaysEqual(object):
            def __eq__(self, other):
                return True

        class NeverEqual(object):
            def __eq__(self, other):
                return False
        for test_range in ranges:
            # test int and thing-that-behaves-like-int-but-is-not
            test_length = len(test_range)
            for cls in (int, Wrapper):
                with self.subTest(test_range=test_range, cls=cls):
                    for index in itertools.chain(backport_range(0, test_length), backport_range(-test_length, 0, -1)):
                        self.assertEqual(
                            test_range.index(cls(test_range[index])),
                            self._normalize_index(index, test_length)
                        )
                        self.assertEqual(
                            test_range.index(cls(test_range[index]), 0, test_length),
                            self._normalize_index(index, test_length)
                        )
                        self.assertEqual(
                            test_range.index(cls(test_range[index]), -test_length, None),
                            self._normalize_index(index, test_length)
                        )
                        self.assertEqual(
                            test_range.index(cls(test_range[index]), None, test_length),
                            self._normalize_index(index, test_length)
                        )
                        if index != 0:
                            self.assertEqual(
                                test_range.index(cls(test_range[index]), index - 1, test_length),
                                self._normalize_index(index, test_length)
                            )
                        if index != -1:
                            self.assertEqual(
                                test_range.index(cls(test_range[index]), index, index + 1),
                                self._normalize_index(index, test_length)
                            )
                    for index in itertools.chain(backport_range(0, test_length), backport_range(-test_length, -1, -1)):
                        with self.assertRaises(ValueError):
                            test_range.index(cls(test_range[index]), index + 1)
                        with self.assertRaises(ValueError):
                            test_range.index(cls(test_range[index]), None, index)
                        with self.assertRaises(ValueError):
                            test_range.index(cls(test_range[index]), index, index)
                        with self.assertRaises(ValueError):
                            test_range.index(cls(test_range[index]), index + 1, index)
            # fake value types
            for idx in backport_range(1, test_length - 1):
                self.assertEqual(test_range.index(AlwaysEqual(), idx), idx)
                self.assertEqual(test_range.index(AlwaysEqual(), 0, idx), 0)
            # empty range never contains anything
            with self.assertRaises(ValueError):
                test_range.index(AlwaysEqual(), 0, 0)
            with self.assertRaises(ValueError):
                test_range.index(AlwaysEqual(), test_length, test_length)
            with self.assertRaises(ValueError):
                test_range.index(AlwaysEqual(), 500, 500000)
            # unequal to any value
            with self.assertRaises(ValueError):
                test_range.index(NeverEqual())
            with self.assertRaises(ValueError):
                test_range.index(NeverEqual(), 0, test_length)
