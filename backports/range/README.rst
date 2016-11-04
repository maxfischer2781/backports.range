+++++++++++++++++++++++++++++++++++++
backports.range class from Python 3.3
+++++++++++++++++++++++++++++++++++++

|travis| |codecov|

|pypi| |pypistatus| |pypiversions| |pypiimplementations|

Backports the python 3.X ``range`` class as a replacement for python 2.X ``range``
functions. The ``range`` class is similar to ``xrange`` in that its values are
computed on demand - however, the ``range`` class is actually a lazy sequence:
it supports indexing, membership testing and other sequence features.

Thus, it can be used to replace both `range` and `xrange`.


.. |travis| image:: https://travis-ci.org/maxfischer2781/backports.range.svg?branch=master
    :target: https://travis-ci.org/maxfischer2781/backports.range
    :alt: Unit Tests

.. |pypi| image:: https://img.shields.io/pypi/v/backports.range.svg
    :target: https://pypi.python.org/pypi/backports.range
    :alt: PyPI Package

.. |pypistatus| image:: https://img.shields.io/pypi/status/backports.range.svg
    :target: https://pypi.python.org/pypi/backports.range
    :alt: PyPI Status

.. |pypiversions| image:: https://img.shields.io/pypi/pyversions/backports.range.svg
    :target: https://pypi.python.org/pypi/backports.range
    :alt: PyPI Versions

.. |pypiimplementations| image:: https://img.shields.io/pypi/implementation/backports.range.svg
    :target: https://pypi.python.org/pypi/backports.range
    :alt: PyPI Implementations

.. |codecov| image:: https://codecov.io/gh/maxfischer2781/backports.range/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/maxfischer2781/backports.range
  :alt: Code Coverage

.. contents:: **Table of Contents**
    :depth: 2

Features
--------

This implementation provides all features introduced and documented in
python 3.3.

All objects are available by default in a pure python implementation.
In addition, there are optional, optimized implementations using `Cython`_.

Performance
^^^^^^^^^^^

The ``backports.range`` is adequate in performance for most applications.
It is comparable in speed to builtins when using `PyPy`_ or `Cython`_, but somewhat slower for small ranges of less than 1000 elements.
This should not be noticeable in all but the most high-performance applications.

When using CPython (aka plain ``python``), pure python mode is considerably slower than the builtins.
Again, this should not matter for most applications, but the use of `Cython`_ is **strongly** advised.

Benchmark for ``[a for a in range(...)]``
.........................................

=============== ================= ==================
Interpreter     vs Builtin range  vs Builtin xrange
=============== ================= ==================
Py2                           100                 50
Py3                       25 - 30                ---
Py2 + Cython                3 - 6            1.0 - 3
Py3 + Cython              1.1 - 3                ---
PyPy2                   1.6 - 2.5          1.6 - 2.3
PyPy3                   0.9 - 1.2                ---
=============== ================= ==================

Cython Optimizations
^^^^^^^^^^^^^^^^^^^^

All `Cython`_ optimizations are optional.
They are automatically made available if `Cython`_ is installed.

- Iteration of C

Compatibility
-------------

- Features are tested against the Python 3.6 unittests for ``range``.

- The following python versions are tested explicitly:

  - CPython (aka python): 2.6, 2.7, 3.2, 3.3, 3.4, 3.5

  - `Cython`_: All versions supported by cpython

  - `PyPy`_: pypy2, pypy3

- Some features depending on language features or other modules may not be
  available or work differently:

  - Comparing ``range`` against other types does not throw ``TypeError`` in python 2.X.

Notice
------

    This packages includes parts of the python documentation (http://www.python.org)
    Copyright (C) 2001-2016 Python Software Foundation.
    Licensed under the Python Software Foundation License.

.. _Cython: http://cython.org

.. _PyPy: http://pypy.org
