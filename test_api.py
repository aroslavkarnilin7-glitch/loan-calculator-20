import pytest
import json
import urllib.error
import socket
from unittest.mock import patch, MagicMock
import api

@patch('urllib.request.urlopen')
def test_fetch_rates_success(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({"Valute": {"USD": {"Value": 90.0}}}).encode('utf-8')
    mock_urlopen.return_value.__enter__.return_value = mock_response
    result = api.fetch_rates()
    assert "Valute" in result

@patch('urllib.request.urlopen')
def test_fetch_rates_success_without_success_field(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({"Valute": {}}).encode('utf-8')
    mock_urlopen.return_value.__enter__.return_value = mock_response
    result = api.fetch_rates()
    assert "Valute" in result

@patch('urllib.request.urlopen')
def test_fetch_rates_http_error(mock_urlopen):
    mock_urlopen.side_effect = urllib.error.HTTPError("url", 404, "Not Found", {}, None)
    with pytest.raises(urllib.error.HTTPError):
        api.fetch_rates()

@patch('urllib.request.urlopen')
def test_fetch_rates_connection_error(mock_urlopen):
    mock_urlopen.side_effect = urllib.error.URLError("Connection error")
    with pytest.raises(urllib.error.URLError):
        api.fetch_rates()

@patch('urllib.request.urlopen')
def test_fetch_rates_timeout_error(mock_urlopen):
    mock_urlopen.side_effect = socket.timeout("Timeout")
    with pytest.raises(socket.timeout):
        api.fetch_rates()

@patch('urllib.request.urlopen')
def test_fetch_rates_empty_valute(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({"Valute": {}}).encode('utf-8')
    mock_urlopen.return_value.__enter__.return_value = mock_response
    result = api.fetch_rates()
    assert result["Valute"] == {}

@patch('urllib.request.urlopen')
def test_fetch_rates_malformed_json(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = b"Not a JSON"
    mock_urlopen.return_value.__enter__.return_value = mock_response
    with pytest.raises(json.JSONDecodeError):
        api.fetch_rates()

@patch('urllib.request.urlopen')
def test_fetch_rates_ssl_error(mock_urlopen):
    mock_urlopen.side_effect = urllib.error.URLError(reason="SSL Error")
    with pytest.raises(urllib.error.URLError):
        api.fetch_rates()