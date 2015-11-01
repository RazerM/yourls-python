# coding: utf-8
from __future__ import absolute_import, division, print_function

from .core import DBStats, ShortenedURL, YOURLSClient, logger
from .exc import (
    YOURLSAPIError, YOURLSHTTPError, YOURLSKeywordExistsError,
    YOURLSNoLoopError, YOURLSNoURLError, YOURLSURLExistsError)

__author__ = 'Frazer McLean <frazer@frazermclean.co.uk>'
__version__ = '1.0.0'
__license__ = 'MIT'
__description__ = 'Python client for YOURLS.'

__all__ = (
    'DBStats',
    'logger',
    'ShortenedURL',
    'YOURLSAPIError',
    'YOURLSClient',
    'YOURLSHTTPError',
    'YOURLSKeywordExistsError',
    'YOURLSNoLoopError',
    'YOURLSNoURLError',
    'YOURLSURLExistsError',
)
