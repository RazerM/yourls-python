# coding: utf-8
from __future__ import absolute_import, division, print_function

import datetime
import sys

import pytest
from yourls import DBStats, ShortenedURL, YOURLSAPIError, YOURLSURLExistsError
from yourls.__main__ import cli, main

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@pytest.fixture(scope='module')
def set_defaults():
    """We load the option defaults from config files; reset the defaults here
    so we can test.
    """
    for param in cli.params:
        param.default = None


def test_cli(set_defaults, capsys):
    argv = ['', 'shorten']
    patch_argv = patch.object(sys, 'argv', argv)
    patch_shorten = patch('yourls.core.YOURLSAPIMixin.shorten', autospec=True)

    with patch_argv, patch_shorten as mock_shorten:
        with pytest.raises(SystemExit):
            main()
        _, err = capsys.readouterr()
        assert 'apiurl missing' in err
        assert mock_shorten.called == 0

    argv = ['', '--apiurl', 'http://example.com', '--username', 'u', 'shorten']
    patch_argv = patch.object(sys, 'argv', argv)

    with patch_argv, patch_shorten as mock_shorten:
        with pytest.raises(SystemExit):
            main()
        out, err = capsys.readouterr()
        assert 'authentication paremeters overspecified' in err
        assert not mock_shorten.called


def test_shorten(set_defaults, capsys):
    argv = ['', '--apiurl', 'http://example.com/yourls-api.php', 'shorten',
            'http://google.com']

    shorturl = ShortenedURL(
        shorturl='http://example.com/abcde',
        url='http://google.com',
        title='Google',
        date=datetime.datetime(2015, 10, 31, 14, 31, 4),
        ip='203.0.113.0',
        clicks=0,
        keyword='abcde')

    patch_argv = patch.object(sys, 'argv', argv)
    patch_shorten = patch(
        'yourls.core.YOURLSAPIMixin.shorten', autospec=True,
        return_value=shorturl)

    with patch_argv, patch_shorten as mock_shorten:
        with pytest.raises(SystemExit):
            main()
        out, _ = capsys.readouterr()
        expected = (
            "New: ShortenedURL(shorturl='http://example.com/abcde', "
            "url='http://google.com', title='Google', "
            "date=datetime.datetime(2015, 10, 31, 14, 31, 4), "
            "ip='203.0.113.0', clicks=0, keyword='abcde')\n")
        assert expected == out
        assert mock_shorten.call_count == 1

    argv = ['', '--apiurl', 'http://example.com/yourls-api.php', 'shorten',
            'http://google.com', '--only-new']
    patch_argv = patch.object(sys, 'argv', argv)
    with patch_argv, patch_shorten as mock_shorten:
        with pytest.raises(SystemExit):
            main()
        out, _ = capsys.readouterr()
        expected = (
            "ShortenedURL(shorturl='http://example.com/abcde', "
            "url='http://google.com', title='Google', "
            "date=datetime.datetime(2015, 10, 31, 14, 31, 4), "
            "ip='203.0.113.0', clicks=0, keyword='abcde')\n")
        assert expected == out
        assert mock_shorten.call_count == 1

    exists_error = YOURLSURLExistsError(
        'http://google.com already exists in database', url=shorturl)

    patch_shorten = patch(
        'yourls.core.YOURLSAPIMixin.shorten', autospec=True,
        side_effect=[exists_error])

    with patch_argv, patch_shorten as mock_shorten:
        with pytest.raises(SystemExit):
            main()
        _, err = capsys.readouterr()
        assert err == 'Error: http://google.com already exists in database\n'

    argv = ['', '--apiurl', 'http://example.com/yourls-api.php', 'shorten',
            'http://google.com', '--simple']
    patch_argv = patch.object(sys, 'argv', argv)

    with patch_argv, patch_shorten as mock_shorten:
        with pytest.raises(SystemExit):
            main()
        out, _ = capsys.readouterr()
        assert out == 'Exists: http://example.com/abcde\n'

    error = YOURLSAPIError('Unknown error')

    patch_shorten = patch(
        'yourls.core.YOURLSAPIMixin.shorten', autospec=True,
        side_effect=[error])

    with patch_argv, patch_shorten as mock_shorten:
        with pytest.raises(SystemExit):
            main()
        _, err = capsys.readouterr()
        assert err == 'Error: Unknown error\n'


def test_expand(set_defaults, capsys):
    argv = ['', '--apiurl', 'http://example.com/yourls-api.php', 'expand',
            'http://example.com/abcde']

    patch_argv = patch.object(sys, 'argv', argv)
    patch_expand = patch(
        'yourls.core.YOURLSAPIMixin.expand', autospec=True,
        return_value='http://google.com')

    with patch_argv, patch_expand as mock_expand:
        with pytest.raises(SystemExit):
            main()
        out, _ = capsys.readouterr()
        expected = "http://google.com\n"
        assert expected == out
        assert mock_expand.call_count == 1

    error = YOURLSAPIError('Unknown error')

    patch_expand = patch(
        'yourls.core.YOURLSAPIMixin.expand', autospec=True,
        side_effect=[error])

    with patch_argv, patch_expand as mock_expand:
        with pytest.raises(SystemExit):
            main()
        _, err = capsys.readouterr()
        assert err == 'Error: Unknown error\n'


def test_url_stats(set_defaults, capsys):
    argv = ['', '--apiurl', 'http://example.com/yourls-api.php', 'url-stats',
            'http://example.com/abcde']

    shorturl = ShortenedURL(
        shorturl='http://example.com/abcde',
        url='http://google.com',
        title='Google',
        date=datetime.datetime(2015, 10, 31, 14, 31, 4),
        ip='203.0.113.0',
        clicks=0,
        keyword='abcde')

    patch_argv = patch.object(sys, 'argv', argv)
    patch_url_stats = patch(
        'yourls.core.YOURLSAPIMixin.url_stats', autospec=True,
        return_value=shorturl)

    with patch_argv, patch_url_stats as mock_url_stats:
        with pytest.raises(SystemExit):
            main()
        out, _ = capsys.readouterr()
        expected = (
            "ShortenedURL(shorturl='http://example.com/abcde', "
            "url='http://google.com', title='Google', "
            "date=datetime.datetime(2015, 10, 31, 14, 31, 4), "
            "ip='203.0.113.0', clicks=0, keyword='abcde')\n")
        assert expected == out
        assert mock_url_stats.call_count == 1


def test_stats(set_defaults, capsys):
    argv = ['', '--apiurl', 'http://example.com/yourls-api.php', 'stats',
            'top', '3']

    links = [
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

    stats = DBStats(total_links=200, total_clicks=5000)

    patch_argv = patch.object(sys, 'argv', argv)
    patch_stats = patch(
        'yourls.core.YOURLSAPIMixin.stats', autospec=True,
        return_value=(links, stats))

    with patch_argv, patch_stats as mock_stats:
        with pytest.raises(SystemExit):
            main()
        out, _ = capsys.readouterr()
        expected = (
            "DBStats(total_clicks=5000, total_links=200)\n"

            "ShortenedURL(shorturl='http://example.com/abcde', "
            "url='http://google.com', title='Google', "
            "date=datetime.datetime(2014, 9, 8, 20, 30, 17), "
            "ip='203.0.113.0', clicks=789)\n"

            "ShortenedURL(shorturl='http://example.com/abc45', "
            "url='https://www.bbc.co.uk/news', title='BBC News', "
            "date=datetime.datetime(2014, 12, 19, 16, 26, 39), "
            "ip='203.0.113.0', clicks=1364)\n"

            "ShortenedURL(shorturl='http://example.com/123de', "
            "url='https://www.youtube.com', title='YouTube', "
            "date=datetime.datetime(2015, 10, 9, 5, 46, 27), "
            "ip='203.0.113.0', clicks=27)\n")
        assert expected == out
        assert mock_stats.call_count == 1

    argv = ['', '--apiurl', 'http://example.com/yourls-api.php', 'stats',
            'top', '3', '--simple']
    patch_argv = patch.object(sys, 'argv', argv)

    with patch_argv, patch_stats as mock_stats:
        with pytest.raises(SystemExit):
            main()
        out, _ = capsys.readouterr()
        expected = (
            "DBStats(total_clicks=5000, total_links=200)\n"
            "http://example.com/abcde\n"
            "http://example.com/abc45\n"
            "http://example.com/123de\n")
        assert expected == out
        assert mock_stats.call_count == 1


def test_db_stats(set_defaults, capsys):
    argv = ['', '--apiurl', 'http://example.com/yourls-api.php', 'db-stats']

    db_stats = DBStats(total_links=200, total_clicks=5000)

    patch_argv = patch.object(sys, 'argv', argv)
    patch_db_stats = patch(
        'yourls.core.YOURLSAPIMixin.db_stats', autospec=True,
        return_value=db_stats)

    with patch_argv, patch_db_stats as mock_db_stats:
        with pytest.raises(SystemExit):
            main()
        out, _ = capsys.readouterr()
        expected = "DBStats(total_clicks=5000, total_links=200)\n"
        assert expected == out
        assert mock_db_stats.call_count == 1
