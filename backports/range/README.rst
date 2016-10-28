backports.range class from Python 3.3
=====================================

Backports the python 3.X `range` class as a replacement for python 2.X `range`
functions. The `range` class is similar to `xrange` in that its values are
computed on demand - however, the `range` class is actually a lazy sequence:
it supports indexing, membership testing and other sequence features.

Features
--------

This implementation provides all features introduced and documented in
python 3.3.

Compatibility
-------------

- Features are tested against the Python 3.6 unittests for `range`.

- The following python versions are tested explicitly:

   - python (aka CPython): 2.6, 2.7, 3.2, 3.3, 3.4, 3.5

   - pypy: pypy2, pypy3

- There is no official support for Cython yet.

- Some features depending on language features or other modules may not be
  available:

   - Comparing `range` against other types does not throw `TypeError` in python 2.X.

Notice
------
This packages includes parts of the python documentation (http://www.python.org)
Copyright (C) 2001-2016 Python Software Foundation.
Licensed under the Python Software Foundation License.