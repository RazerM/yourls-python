# coding: utf-8
from __future__ import absolute_import, division, print_function

import datetime
import sys

import pytest
from yourls import ShortenedURL, YOURLSURLExistsError, YOURLSAPIError
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
        with pytest.raises(SystemExit) as exc_info:
            main()
        _, err = capsys.readouterr()
        assert 'apiurl missing' in err
        assert mock_shorten.called == 0

    argv = ['', '--apiurl', 'http://example.com', '--username', 'u', 'shorten']
    patch_argv = patch.object(sys, 'argv', argv)

    with patch_argv, patch_shorten as mock_shorten:
        with pytest.raises(SystemExit) as exc_info:
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
