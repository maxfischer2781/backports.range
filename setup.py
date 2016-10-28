# -*- coding: utf-8 -*-
from __future__ import with_statement
import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'backports', 'range', 'README.rst')) as readme:
    long_description = readme.read()

setup(
    name='backports.range',
    version='3.3.0',
    description='Backport of the python 3.X `range` class',
    long_description=long_description,
    author='Max Fischer',
    author_email='maxfischer2781@gmail.com',
    url='https://github.com/maxfischer2781/backports.range.git',
    license='MIT',
    namespace_packages=['backports'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        ],
    package_data={'backports': ['range/README.rst', 'range/LICENSE.txt']},
    packages=find_packages(exclude=('backports_*',)),
    test_suite='backports_range_unittests',
    )
