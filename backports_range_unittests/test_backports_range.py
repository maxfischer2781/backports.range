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
    @unittest.skipUnless(type(range(1)) == range, "no builtin range class")
    @unittest.skipUnless(range(0, 27) == range(0, 27), "no equality defined for builtin range")
    def test_compare_builtin(self):
        """Compatibility: backport range equal to builtin range"""
        init_args = (
            # start only
            (27,), (15,), (128,), (-127,),
            # default step ranges
            (1, 2), (-50, 50, 1), (-256, -255),
            (-9223372036854775809, -9223372036854775807), (9223372036854775807, 9223372036854775809),
            # empty
            (1, 1, 1), (20, 0, 1), (0, 50, -1), (0, 0),
            # regular ranges
            (1, 120, 5))
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
