# coding: utf-8
from __future__ import absolute_import, division, print_function

import sys
from datetime import datetime

import requests
import six
from logbook import Logger
from represent import ReprHelperMixin
from requests import HTTPError

from .exc import (
    YOURLSAPIError, YOURLSHTTPError, YOURLSKeywordExistsError,
    YOURLSNoLoopError, YOURLSNoURLError, YOURLSURLExistsError)

logger = Logger('yourls')
logger.disabled = True


class ShortenedURL(ReprHelperMixin, object):
    """Represent shortened URL data as returned by the YOURLS API.

    .. attribute:: keyword

       Short URL keyword, e.g. ``abcdef`` for ``http://example.com/abcdef``.

    .. attribute:: url

       Long URL that was shortened.

    .. attribute:: title

       URL page title.

    .. attribute:: date

       :py:class:`~datetime.datetime` of timestamp the URL was shortened.

    .. attribute:: ip

       IP address that originally shortened the URL.

    .. attribute:: clicks

       Number of clicks the shortened URL has received.

    """
    __slots__ = ('shorturl', 'url', 'title', 'date', 'ip', 'clicks', 'keyword')

    def __init__(self, shorturl, url, title, date, ip, clicks, keyword=None):
        self.shorturl = shorturl
        self.url = url
        self.title = title
        self.date = date
        self.ip = ip
        self.clicks = clicks
        self.keyword = keyword

    def _repr_helper_(self, r):
        r.keyword_from_attr('shorturl')
        r.keyword_from_attr('url')
        r.keyword_from_attr('title')
        r.keyword_from_attr('date')
        r.keyword_from_attr('ip')
        r.keyword_from_attr('clicks')
        if self.keyword is not None:
            r.keyword_from_attr('keyword')

    def __eq__(self, other):
        if isinstance(other, ShortenedURL):
            params = ('shorturl', 'url', 'title', 'date', 'ip', 'clicks', 'keyword')
            return all(getattr(self, p) == getattr(other, p) for p in params)
        else:
            return NotImplemented


class DBStats(ReprHelperMixin, object):
    __slots__ = ('total_clicks', 'total_links')

    def __init__(self, total_clicks, total_links):
        self.total_clicks = total_clicks
        self.total_links = total_links

    def _repr_helper_(self, r):
        r.keyword_from_attr('total_clicks')
        r.keyword_from_attr('total_links')

    def __eq__(self, other):
        if isinstance(other, DBStats):
            params = ('total_clicks', 'total_links')
            return all(getattr(self, p) == getattr(other, p) for p in params)
        else:
            return NotImplemented


def _handle_api_error_with_json(http_exc, jsondata, response):
    """Handle YOURLS API errors.

    requests' raise_for_status doesn't show the user the YOURLS json response,
    so we parse that here and raise nicer exceptions.
    """
    if 'code' in jsondata and 'message' in jsondata:
        code = jsondata['code']
        message = jsondata['message']

        if code == 'error:noloop':
            raise YOURLSNoLoopError(message, response=response)
        elif code == 'error:nourl':
            raise YOURLSNoURLError(message, response=response)

    elif 'message' in jsondata:
        message = jsondata['message']
        raise YOURLSHTTPError(message, response=response)

    http_error_message = http_exc.args[0]
    raise YOURLSHTTPError(http_error_message, response=response)


def _validate_yourls_response(response, data):
    """Validate response from YOURLS server."""
    try:
        response.raise_for_status()
    except HTTPError as http_exc:
        # Collect full HTTPError information so we can reraise later if required.
        http_error_info = sys.exc_info()

        # We will reraise outside of try..except block to prevent exception
        # chaining showing wrong traceback when we try and parse JSON response.
        reraise = False

        try:
            jsondata = response.json()
        except ValueError:
            reraise = True
        else:
            logger.debug('Received error {response} with JSON {json}',
                         response=response, json=jsondata)
            _handle_api_error_with_json(http_exc, jsondata, response)

        if reraise:
            six.reraise(*http_error_info)
    else:
        # We have a valid HTTP response, but we need to check what the API says
        # about the request.
        jsondata = response.json()

        logger.debug('Received {response} with JSON {json}', response=response,
                     json=jsondata)

        if 'status' in jsondata and 'code' in jsondata:
            status = jsondata['status']
            code = jsondata['code']
            message = jsondata['message']

            if status == 'fail':
                if code == 'error:keyword':
                    raise YOURLSKeywordExistsError(message, keyword=data['keyword'])
                elif code == 'error:url':
                    url = _json_to_shortened_url(jsondata['url'], jsondata['shorturl'])
                    raise YOURLSURLExistsError(message, url=url)
                else:
                    raise YOURLSAPIError(message)
            else:
                return jsondata
        else:
            # Without status, nothing special needs to be handled.
            return jsondata


def _json_to_shortened_url(urldata, shorturl=None):
    if shorturl is None:
        shorturl = urldata['shorturl']

    if 'date' in urldata:
        date = urldata['date']
    elif 'timestamp' in urldata:
        date = urldata['timestamp']
    else:
        raise ValueError("Expected 'date' or 'timestamp' key in urldata.")

    keyword = urldata.get('keyword', None)

    clicks = int(urldata.get('clicks', '0'))

    url = ShortenedURL(
        shorturl=shorturl,
        url=urldata['url'],
        title=urldata['title'],
        date=datetime.strptime(date, '%Y-%m-%d %H:%M:%S'),
        ip=urldata['ip'],
        clicks=clicks,
        keyword=keyword)

    return url


class YOURLSClient(object):
    """YOURLS client."""
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

    def shorten(self, url, keyword=None, title=None):
        """Shorten URL with optional keyword and title.

        Parameters:
            url: URL to shorten.
            keyword: Optionally choose keyword for short URL, otherwise automatic.
            title: Optionally choose title, otherwise taken from web page.

        Returns:
            ShortenedURL: Shortened URL and associated data.

        Raises:
            ~yourls.exc.YOURLSKeywordExistsError: The passed keyword already exists.

                .. note::

                    This exception has a ``keyword`` attribute.

            ~yourls.exc.YOURLSURLExistsError: The URL has already been shortened.

                .. note::

                    This exception has a ``url`` attribute, which is an instance
                    of :py:class:`ShortenedURL` for the existing short URL.

            ~yourls.exc.YOURLSNoURLError: URL missing.

            ~yourls.exc.YOURLSNoLoopError: Cannot shorten a shortened URL.

            ~yourls.exc.YOURLSAPIError: Unhandled API error.

            ~yourls.exc.YOURLSHTTPError: HTTP error with response from YOURLS API.

            requests.HTTPError: Generic HTTP error.
        """
        data = dict(action='shorturl', url=url, keyword=keyword, title=title)
        jsondata = self._api_request(params=data)

        url = _json_to_shortened_url(jsondata['url'], jsondata['shorturl'])

        return url

    def expand(self, short):
        """Expand short URL or keyword to long URL.

        Parameters:
            short: Short URL (http://example.com/abc) or keyword (abc).

        :return: Expanded/long URL, e.g. https://www.youtube.com/watch?v=dQw4w9WgXcQ

        Raises:
            ~yourls.exc.YOURLSHTTPError: HTTP error with response from YOURLS API.
            requests.HTTPError: Generic HTTP error.
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
            ~yourls.exc.YOURLSHTTPError: HTTP error with response from YOURLS API.
            requests.HTTPError: Generic HTTP error.
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
            requests.HTTPError: Generic HTTP Error
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
            requests.HTTPError: Generic HTTP Error
        """
        data = dict(action='db-stats')
        jsondata = self._api_request(params=data)

        stats = DBStats(total_clicks=int(jsondata['db-stats']['total_clicks']),
                        total_links=int(jsondata['db-stats']['total_links']))

        return stats
