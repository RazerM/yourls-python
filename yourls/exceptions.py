# coding: utf-8
from __future__ import absolute_import, division, print_function

from requests import HTTPError


class YOURLSAPIError(Exception):
    """Base exception."""
    def __init__(self, *args, **kwargs):
        super(YOURLSAPIError, self).__init__(*args, **kwargs)


class YOURLSHTTPError(YOURLSAPIError, HTTPError):
    """Raised when YOURLS API returns HTTP error with response."""
    def __init__(self, *args, **kwargs):
        super(YOURLSAPIError, self).__init__(*args, **kwargs)


class YOURLSNoLoopError(YOURLSHTTPError):
    """Raised when trying to shorten a shortened URL."""
    def __init__(self, *args, **kwargs):
        super(YOURLSAPIError, self).__init__(*args, **kwargs)


class YOURLSNoURLError(YOURLSHTTPError):
    """Raised when trying to shorten an empty URL."""
    def __init__(self, *args, **kwargs):
        super(YOURLSAPIError, self).__init__(*args, **kwargs)


class YOURLSKeywordExistsError(YOURLSAPIError):
    """Raised when a chosen keyword already exists.

    .. attribute:: keyword

       Existing keyword.

    """
    def __init__(self, *args, **kwargs):
        self.keyword = kwargs.pop('keyword')
        super(YOURLSAPIError, self).__init__(*args, **kwargs)


class YOURLSURLExistsError(YOURLSAPIError):
    """Raised when a URL has already been shortened.

    .. attribute:: url

       Instance of :py:class:`~yourls.data.ShortenedURL` for existing URL.
    """
    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop('url')
        super(YOURLSAPIError, self).__init__(*args, **kwargs)
