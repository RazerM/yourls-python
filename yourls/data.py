# coding: utf-8
from __future__ import absolute_import, division, print_function

import sys
from datetime import datetime

import six
from represent import ReprHelperMixin
from requests import HTTPError

from .exceptions import (
    YOURLSAPIError, YOURLSHTTPError, YOURLSKeywordExistsError,
    YOURLSNoLoopError, YOURLSNoURLError, YOURLSURLExistsError)
from .log import logger


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
    """Represent database statistics as returned by the YOURLS API.

    .. attribute:: total_clicks

       Total number of clicks across all links in the database.

    .. attribute:: total_links

       Total number of links in the database.
    """
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

        if {'status', 'code', 'message'} <= set(jsondata.keys()):
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
        raise YOURLSAPIError("Expected 'date' or 'timestamp' key in JSON response.")

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
