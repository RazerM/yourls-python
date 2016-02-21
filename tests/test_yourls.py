# coding: utf-8
from __future__ import absolute_import, division, print_function

import datetime

import pytest
import requests
import responses
from responses import GET
from yourls import (
    DBStats, ShortenedURL, YOURLSAPIError, YOURLSClient, YOURLSHTTPError,
    YOURLSKeywordExistsError, YOURLSNoLoopError, YOURLSNoURLError,
    YOURLSURLExistsError)


@pytest.yield_fixture(scope='module')
def yourls():
    yield YOURLSClient(apiurl='http://example.com/yourls-api.php', signature='6f344c2a8p')


def make_url(yourls, params):
    params = params.copy()
    params.update(yourls._data)
    return requests.Request('GET', yourls.apiurl, params=params).prepare().url


def test_authentication_parameters():

    apiurl = 'http://example.com/yourls-api.php'

    # Public server requires no authentication, shouldn't raise an exception
    YOURLSClient(apiurl)

    # signature or username and password is correct way to authenticate
    YOURLSClient(apiurl, signature='abcdefghij')
    YOURLSClient(apiurl, username='user', password='pass')

    # Specifying signature and username of password is incorrect
    with pytest.raises(TypeError):
        YOURLSClient(apiurl, signature='abcdefghij', username='user', password='pass')

    with pytest.raises(TypeError):
        YOURLSClient(apiurl, signature='abcdefghij', username='user')

    with pytest.raises(TypeError):
        YOURLSClient(apiurl, signature='abcdefghij', password='pass')


@responses.activate
def test_shorten_new(yourls):
    url = 'http://google.com'
    params = dict(action='shorturl', url=url)

    json_response = {
        'message': 'http://google.com added to database',
        'shorturl': 'http://example.com/abcde',
        'url': {
            'keyword': 'abcde',
            'ip': '203.0.113.0',
            'title': 'Google',
            'url': 'http://google.com',
            'date': '2015-10-31 14:31:04'
        },
        'status': 'success',
        'title': 'Google',
        'statusCode': 200
    }

    query_url = make_url(yourls, params=params)
    responses.add(GET, query_url, json=json_response, status=200,
                  match_querystring=True)

    actual_short_url = yourls.shorten(url)
    expected_short_url = ShortenedURL(
        shorturl='http://example.com/abcde',
        url='http://google.com',
        title='Google',
        date=datetime.datetime(2015, 10, 31, 14, 31, 4),
        ip='203.0.113.0',
        clicks=0,
        keyword='abcde')

    assert len(responses.calls) == 1
    assert actual_short_url == expected_short_url


@responses.activate
def test_shorten_url_exists(yourls):
    url = 'http://google.com'
    params = dict(action='shorturl', url=url)

    json_response = {
        'title': 'Google',
        'url': {
            'keyword': 'abcde',
            'ip': '203.0.113.0',
            'title': 'Google',
            'url': 'http://google.com',
            'date': '2015-01-01 14:31:04',
            'clicks': '123'
        },
        'statusCode': 200,
        'code': 'error:url',
        'status': 'fail',
        'message': 'http://google.com already exists in database',
        'shorturl': 'http://example.com/abcde'
    }

    query_url = make_url(yourls, params=params)
    responses.add(GET, query_url, json=json_response, status=200,
                  match_querystring=True)

    with pytest.raises(YOURLSURLExistsError) as exc_info:
        yourls.shorten(url)

    actual_short_url = exc_info.value.url
    expected_short_url = ShortenedURL(
        shorturl='http://example.com/abcde',
        url='http://google.com',
        title='Google',
        date=datetime.datetime(2015, 1, 1, 14, 31, 4),
        ip='203.0.113.0',
        clicks=123,
        keyword='abcde')

    assert len(responses.calls) == 1
    assert actual_short_url == expected_short_url


@responses.activate
def test_shorten_keyword_exists(yourls):
    url = 'http://www.bbc.co.uk'
    params = dict(action='shorturl', url=url, keyword='abcde')

    json_response = {
        'statusCode': 200,
        'code': 'error:keyword',
        'message': 'Short URL abcde already exists in database or is reserved',
        'status': 'fail'
    }

    query_url = make_url(yourls, params=params)
    responses.add(GET, query_url, json=json_response, status=200,
                  match_querystring=True)

    with pytest.raises(YOURLSKeywordExistsError) as exc_info:
        yourls.shorten(url, keyword='abcde')

    keyword = exc_info.value.keyword
    assert keyword == 'abcde'


@responses.activate
def test_shorten_nourl(yourls):
    params = dict(action='shorturl', url='')

    json_response = {
        'status': 'fail',
        'message': 'Missing or malformed URL',
        'code': 'error:nourl',
        'errorCode': '400'
    }

    query_url = make_url(yourls, params=params)
    responses.add(GET, query_url, json=json_response, status=400,
                  match_querystring=True)

    with pytest.raises(YOURLSNoURLError):
        yourls.shorten('')


@responses.activate
def test_shorten_shorturl(yourls):
    url = 'http://example.com/abcde'
    params = dict(action='shorturl', url=url)

    json_response = {
        'errorCode': '400',
        'message': 'URL is a short URL',
        'status': 'fail',
        'code': 'error:noloop'
    }

    query_url = make_url(yourls, params=params)
    responses.add(GET, query_url, json=json_response, status=400,
                  match_querystring=True)

    with pytest.raises(YOURLSNoLoopError):
        yourls.shorten(url)


@responses.activate
def test_expand(yourls):
    keyword = 'abcde'
    params = dict(action='expand', shorturl=keyword)
    json_response = {
        'statusCode': 200,
        'shorturl': 'http://fraz.eu/abcde',
        'keyword': 'abcde',
        'message': 'success',
        'longurl': 'http://google.com'
    }

    query_url = make_url(yourls, params=params)
    responses.add(GET, query_url, json=json_response, status=200,
                  match_querystring=True)

    assert yourls.expand(keyword) == 'http://google.com'


@responses.activate
def test_expand_missing(yourls):
    keyword = 'vwxyz'
    params = dict(action='expand', shorturl=keyword)

    json_response = {
        'message': 'Error: short URL not found',
        'keyword': 'vwxyz',
        'errorCode': 404
    }

    query_url = make_url(yourls, params=params)
    responses.add(GET, query_url, json=json_response, status=404,
                  match_querystring=True)

    with pytest.raises(YOURLSHTTPError):
        yourls.expand(keyword)


@responses.activate
def test_url_stats(yourls):
    keyword = 'abcde'
    params = dict(action='url-stats', shorturl=keyword)

    json_response = {
        'link': {
            'title': 'Google',
            'shorturl': 'http://example.com/abcde',
            'ip': '203.0.113.0',
            'timestamp': '2015-10-29 20:36:54',
            'clicks': '356',
            'url': 'http://google.com'
        },
        'statusCode': 200,
        'message': 'success'}

    query_url = make_url(yourls, params=params)
    responses.add(GET, query_url, json=json_response, status=200,
                  match_querystring=True)

    actual_short_url = yourls.url_stats(keyword)
    expected_short_url = ShortenedURL(
        shorturl='http://example.com/abcde',
        url='http://google.com',
        title='Google',
        date=datetime.datetime(2015, 10, 29, 20, 36, 54),
        ip='203.0.113.0',
        clicks=356,
        keyword=None)

    assert actual_short_url == expected_short_url


@responses.activate
def test_url_stats_missing(yourls):
    keyword = 'vwxyz'
    params = dict(action='url-stats', shorturl=keyword)

    json_response = {
        'message': 'Error: short URL not found',
        'keyword': 'vwxyz',
        'errorCode': 404
    }

    query_url = make_url(yourls, params=params)
    responses.add(GET, query_url, json=json_response, status=404,
                  match_querystring=True)

    with pytest.raises(YOURLSHTTPError):
        yourls.url_stats(keyword)


@responses.activate
def test_stats(yourls):
    params = dict(action='stats', filter='rand', limit=3)

    json_response = {
        'message': 'success',
        'stats': {
            'total_links': '200',
            'total_clicks': '5000'
        },
        'links': {
            'link_1': {
                'shorturl': 'http://example.com/abcde',
                'title': 'Google',
                'url': 'http://google.com',
                'timestamp': '2014-09-08 20:30:17',
                'ip': '203.0.113.0',
                'clicks': '789'
            },
            'link_2': {
                'shorturl': 'http://example.com/abc45',
                'title': 'BBC News',
                'url': 'https://www.bbc.co.uk/news',
                'timestamp': '2014-12-19 16:26:39',
                'ip': '203.0.113.0',
                'clicks': '1364'
            },
            'link_3': {
                'shorturl': 'http://example.com/123de',
                'title': 'YouTube',
                'url': 'https://www.youtube.com',
                'timestamp': '2015-10-09 05:46:27',
                'ip': '203.0.113.0',
                'clicks': '27'
            }
        },
        'statusCode': 200
    }

    query_url = make_url(yourls, params=params)
    responses.add(GET, query_url, json=json_response, status=200,
                  match_querystring=True)

    links, stats = yourls.stats(filter='random', limit=3)

    assert links == [
        ShortenedURL(
            shorturl='http://example.com/abcde',
            url='http://google.com',
            title='Google',
            date=datetime.datetime(2014, 9, 8, 20, 30, 17),
            ip='203.0.113.0',
            clicks=789,
            keyword=None),
        ShortenedURL(
            shorturl='http://example.com/abc45',
            url='https://www.bbc.co.uk/news',
            title='BBC News',
            date=datetime.datetime(2014, 12, 19, 16, 26, 39),
            ip='203.0.113.0',
            clicks=1364,
            keyword=None),
        ShortenedURL(
            shorturl='http://example.com/123de',
            url='https://www.youtube.com',
            title='YouTube',
            date=datetime.datetime(2015, 10, 9, 5, 46, 27),
            ip='203.0.113.0',
            clicks=27,
            keyword=None)
    ]

    assert stats == DBStats(total_links=200, total_clicks=5000)


@responses.activate
def test_stats_zero(yourls):
    params = dict(action='stats', filter='top', limit=0)

    json_response = {
        'message': 'success',
        'stats': {
            'total_links': '200',
            'total_clicks': '5000'
        },
        'links': {},
        'statusCode': 200
    }

    query_url = make_url(yourls, params=params)
    responses.add(GET, query_url, json=json_response, status=200,
                  match_querystring=True)

    links, stats = yourls.stats(filter='top', limit=0)

    assert links == []

    assert stats == DBStats(total_links=200, total_clicks=5000)


def test_stats_invalid_filter(yourls):
    with pytest.raises(ValueError):
        yourls.stats(filter='Midnight', limit=5)


@responses.activate
def test_db_stats(yourls):
    params = dict(action='db-stats')

    json_response = {
        'message': 'success',
        'statusCode': 200,
        'db-stats': {
            'total_links': '200',
            'total_clicks': '5000'
        }
    }

    query_url = make_url(yourls, params=params)
    responses.add(GET, query_url, json=json_response, status=200,
                  match_querystring=True)

    stats = yourls.db_stats()
    assert stats == DBStats(total_links=200, total_clicks=5000)


def test_repr():
    shorturl = ShortenedURL(
        shorturl='a',
        url='b',
        title='c',
        date=datetime.datetime(2015, 1, 1, 0, 0, 0),
        ip='203.0.113.0',
        clicks=0,
        keyword='d')

    reprstr = ("ShortenedURL(shorturl='a', url='b', title='c', "
               "date=datetime.datetime(2015, 1, 1, 0, 0), ip='203.0.113.0', "
               "clicks=0, keyword='d')")

    assert repr(shorturl) == reprstr

    shorturl.keyword = None
    reprstr = ("ShortenedURL(shorturl='a', url='b', title='c', "
               "date=datetime.datetime(2015, 1, 1, 0, 0), "
               "ip='203.0.113.0', clicks=0)")
    assert repr(shorturl) == reprstr

    stats = DBStats(total_clicks=5000, total_links=200)
    reprstr = 'DBStats(total_clicks=5000, total_links=200)'
    assert repr(stats) == reprstr


@responses.activate
def test_unknown_json_errors(yourls):
    params = dict(action='shorturl', url='http://google.com')

    json_response = {
        'status': 'fail',
        'message': 'The error is fictitious.',
        'code': 'error:madeuperror',
        'errorCode': '400'
    }

    query_url = make_url(yourls, params=params)
    responses.add(GET, query_url, json=json_response, status=400,
                  match_querystring=True)

    with pytest.raises(YOURLSHTTPError):
        yourls.shorten('http://google.com')

    params = dict(action='shorturl', url='http://bbc.co.uk')

    json_response = {
        'status': 'fail',
        'errorCode': '400'
    }

    query_url = make_url(yourls, params=params)
    responses.add(GET, query_url, json=json_response, status=400,
                  match_querystring=True)

    with pytest.raises(YOURLSHTTPError):
        yourls.shorten('http://bbc.co.uk')

    params = dict(action='shorturl', url='http://gov.uk')

    json_response = {
        'title': 'Google',
        'url': {
            'keyword': 'abcde',
            'ip': '203.0.113.0',
            'title': 'Google',
            'url': 'http://google.com',
            'date': '2015-01-01 14:31:04',
            'clicks': '123'
        },
        'statusCode': 200,
        'code': 'error:dragons',
        'status': 'fail',
        'message': 'http://google.com already exists in database',
        'shorturl': 'http://example.com/abcde'
    }

    query_url = make_url(yourls, params=params)
    responses.add(GET, query_url, json=json_response, status=200,
                  match_querystring=True)

    with pytest.raises(YOURLSAPIError):
        yourls.shorten('http://gov.uk')

    params = dict(action='shorturl', url='http://youtube.com')

    json_response = {
        'message': 'http://google.com added to database',
        'shorturl': 'http://example.com/abcde',
        'url': {
            'keyword': 'abcde',
            'ip': '203.0.113.0',
            'title': 'Google',
            'url': 'http://google.com',
        },
        'status': 'success',
        'title': 'Google',
        'statusCode': 200
    }

    query_url = make_url(yourls, params=params)
    responses.add(GET, query_url, json=json_response, status=200,
                  match_querystring=True)

    with pytest.raises(YOURLSAPIError):
        yourls.shorten('http://youtube.com')


@responses.activate
def test_unknown_errors(yourls):
    params = dict(action='shorturl', url='http://google.com')

    query_url = make_url(yourls, params=params)
    responses.add(GET, query_url, body='', status=400,
                  match_querystring=True)

    with pytest.raises(requests.HTTPError):
        yourls.shorten('http://google.com')
