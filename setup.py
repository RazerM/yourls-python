# coding: utf-8
from __future__ import absolute_import, division, print_function

import re
import sys

from setuptools import setup, find_packages


INIT_FILE = 'yourls/__init__.py'
init_data = open(INIT_FILE).read()

metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_data))

AUTHOR_EMAIL = metadata['author']
VERSION = metadata['version']
LICENSE = metadata['license']
DESCRIPTION = metadata['description']

AUTHOR, EMAIL = re.match(r'(.*) <(.*)>', AUTHOR_EMAIL).groups()

requires = [
    'click',
    'logbook>=0.10.0',
    'represent>=1.4.0',
    'requests',
    'six',
]

extras_require = {
    'dev': [
        'coverage',
        'doc8',
        'flake8',
        'flake8-coding',
        'flake8-future-import',
        'pep8-naming',
        'plumbum',
        'pyenchant',
        'pytest>=2.7.3',
        'responses',
        'shovel',
        'sphinx',
        'sphinx_rtd_theme',
        'sphinxcontrib-spelling',
        'tox',
        'watchdog',
    ],
}

if sys.version_info[:2] < (3, 3):
    extras_require['dev'].append('mock')

setup(
    name='yourls',
    version=VERSION,
    description=DESCRIPTION,
    long_description=open('README.rst').read(),
    author=AUTHOR,
    author_email=EMAIL,
    url='https://github.com/razerm/yourls-python',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    license=LICENSE,
    install_requires=requires,
    extras_require=extras_require,
    entry_points='''
        [console_scripts]
        yourls=yourls.__main__:cli
    ''')
