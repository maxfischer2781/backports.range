# -*- coding: utf-8 -*-
import os
from setuptools import setup

long_description = open(os.path.join(
    os.path.dirname(__file__), 'backports', 'range', 'README.rst',
    )).read()

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
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        ],
    packages=['backports', 'backports.range'],
    test_suite='backports_range_unittests',
    )
