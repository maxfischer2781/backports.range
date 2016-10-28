# -*- coding: utf-8 -*-
from __future__ import with_statement
import os
from setuptools import setup

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
    license='Python Software Foundation License',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Python Software Foundation License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        ],
    packages=['backports', 'backports.range'],
    test_suite='backports_range_unittests',
    )
