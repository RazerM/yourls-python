# coding: utf-8
from __future__ import absolute_import, division, print_function

import re
import sys
from collections import defaultdict

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand  # noqa


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


extras_require = defaultdict(set)

extras_require['test'] = [
    'pytest>=2.7.3',
    'responses',
]

extras_require['dev'] = [
    'coverage',
    'doc8',
    'flake8',
    'flake8-coding',
    'flake8-future-import',
    'pep8-naming',
    'plumbum',
    'pyenchant',
    'shovel',
    'sphinx',
    'sphinx_rtd_theme',
    'sphinxcontrib-spelling',
    'tox',
    'watchdog',
    'pytest>=2.7.3',
    'responses',
]

extras_require['test:python_version<"3.3"'] = ['mock']
extras_require['dev:python_version<"3.3"'] = ['mock']

extras_require = dict(extras_require)


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='yourls',
    version=VERSION,
    description=DESCRIPTION,
    long_description=open('README.rst').read(),
    author=AUTHOR,
    author_email=EMAIL,
    url='https://github.com/razerm/yourls-python',
    packages=find_packages(exclude=['tests']),
    cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    license=LICENSE,
    install_requires=requires,
    extras_require=extras_require,
    entry_points={
        'console_scripts': [
            'yourls=yourls.__main__:cli'
        ]
    })
