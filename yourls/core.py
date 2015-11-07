# coding: utf-8
from __future__ import absolute_import, division, print_function

import requests

from .data import (
    DBStats, _json_to_shortened_url, _validate_yourls_response)


class YOURLSClientBase(object):
    """Base class for YOURLS client that provides initialiser and api request method."""
    def __init__(self, apiurl, username=None, password=None, signature=None):
        self.apiurl = apiurl
        if username and password and signature is None:
            self._data = dict(username=username, password=password)
        elif username is None and password is None and signature:
            self._data = dict(signature=signature)
        elif username is None and password is None and signature is None:
            self._data = dict()
        else:
            raise TypeError(
                'If server requires authentication, either pass username and '
                'password or signature. Otherwise, leave set to default (None)')

        self._data['format'] = 'json'

    def _api_request(self, params):
        params = params.copy()
        params.update(self._data)

        response = requests.get(self.apiurl, params=params)
        jsondata = _validate_yourls_response(response, params)
        return jsondata


class YOURLSAPIMixin(object):
    """Mixin to provide default YOURLS API methods."""
    def shorten(self, url, keyword=None, title=None):
        """Shorten URL with optional keyword and title.

        Parameters:
            url: URL to shorten.
            keyword: Optionally choose keyword for short URL, otherwise automatic.
            title: Optionally choose title, otherwise taken from web page.

        Returns:
            ShortenedURL: Shortened URL and associated data.

        Raises:
            ~yourls.exceptions.YOURLSKeywordExistsError: The passed keyword
                already exists.

                .. note::

                    This exception has a ``keyword`` attribute.

            ~yourls.exceptions.YOURLSURLExistsError: The URL has already been
                shortened.

                .. note::

                    This exception has a ``url`` attribute, which is an instance
                    of :py:class:`ShortenedURL` for the existing short URL.

            ~yourls.exceptions.YOURLSNoURLError: URL missing.

            ~yourls.exceptions.YOURLSNoLoopError: Cannot shorten a shortened URL.

            ~yourls.exceptions.YOURLSAPIError: Unhandled API error.

            ~yourls.exceptions.YOURLSHTTPError: HTTP error with response from
                YOURLS API.

            requests.exceptions.HTTPError: Generic HTTP error.
        """
        data = dict(action='shorturl', url=url, keyword=keyword, title=title)
        jsondata = self._api_request(params=data)

        url = _json_to_shortened_url(jsondata['url'], jsondata['shorturl'])

        return url

    def expand(self, short):
        """Expand short URL or keyword to long URL.

        Parameters:
            short: Short URL (``http://example.com/abc``) or keyword (abc).

        :return: Expanded/long URL, e.g.
                 ``https://www.youtube.com/watch?v=dQw4w9WgXcQ``

        Raises:
            ~yourls.exceptions.YOURLSHTTPError: HTTP error with response from
                YOURLS API.
            requests.exceptions.HTTPError: Generic HTTP error.
        """
        data = dict(action='expand', shorturl=short)
        jsondata = self._api_request(params=data)

        return jsondata['longurl']

    def url_stats(self, short):
        """Get stats for short URL or keyword.

        Parameters:
            short: Short URL (http://example.com/abc) or keyword (abc).

        Returns:
            ShortenedURL: Shortened URL and associated data.

        Raises:
            ~yourls.exceptions.YOURLSHTTPError: HTTP error with response from
                YOURLS API.
            requests.exceptions.HTTPError: Generic HTTP error.
        """
        data = dict(action='url-stats', shorturl=short)
        jsondata = self._api_request(params=data)

        return _json_to_shortened_url(jsondata['link'])

    def stats(self, filter, limit, start=None):
        """Get stats about links.

        Parameters:
            filter: 'top', 'bottom', 'rand', or 'last'.
            limit: Number of links to return from filter.
            start: Optional start number.

        Returns:
            Tuple containing list of ShortenedURLs and DBStats.

        Example:

            .. code-block:: python

                links, stats = yourls.stats(filter='top', limit=10)

        Raises:
            ValueError: Incorrect value for filter parameter.
            requests.exceptions.HTTPError: Generic HTTP Error
        """
        # Normalise random to rand, even though it's accepted by API.
        if filter == 'random':
            filter = 'rand'

        valid_filters = ('top', 'bottom', 'rand', 'last')
        if filter not in valid_filters:
            msg = 'filter must be one of {}'.format(', '.join(valid_filters))
            raise ValueError(msg)

        data = dict(action='stats', filter=filter, limit=limit, start=start)
        jsondata = self._api_request(params=data)

        stats = DBStats(total_clicks=int(jsondata['stats']['total_clicks']),
                        total_links=int(jsondata['stats']['total_links']))

        links = []

        if 'links' in jsondata:
            for i in range(1, limit + 1):
                key = 'link_{}'.format(i)
                links.append(_json_to_shortened_url(jsondata['links'][key]))

        return links, stats

    def db_stats(self):
        """Get database statistics.

        Returns:
            DBStats: Total clicks and links statistics.

        Raises:
            requests.exceptions.HTTPError: Generic HTTP Error
        """
        data = dict(action='db-stats')
        jsondata = self._api_request(params=data)

        stats = DBStats(total_clicks=int(jsondata['db-stats']['total_clicks']),
                        total_links=int(jsondata['db-stats']['total_links']))

        return stats


class YOURLSClient(YOURLSAPIMixin, YOURLSClientBase):
    """YOURLS client."""
