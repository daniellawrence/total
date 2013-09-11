#!/usr/bin/env python
from distutils.core import setup
import os
import setuptools

README = "/".join([os.path.dirname(__file__), "README.md"])

try:
    with open(README) as file:
        long_description = file.read()
except IOError:
    long_description = ''

setup(
    name='total',
    version='0.0.4',
    description='Simple AWK tasks, made awesome',
    author='Danny Lawrence',
    author_email='dannyla@linux.com',
    url='https://github.com/daniellawrence/total',
    packages=['total'],
    long_description=long_description,
    entry_points = {
        'console_scripts': [
            'total = total.total:main'
            ]
        }
)
