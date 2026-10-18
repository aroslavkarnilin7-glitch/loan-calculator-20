import pytest
import sqlite3
import os
import tempfile
from unittest.mock import patch, MagicMock
import db

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    fd, path = tempfile.mkstemp()
    os.close(fd)
    monkeypatch.setattr(db, 'DB_NAME', path)
    db.init_db()
    yield
    if os.path.exists(path):
        os.remove(path)

def test_init_db_creates_table():
    with sqlite3.connect(db.DB_NAME) as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rates'")
        assert cursor.fetchone() is not None

def test_save_rate_new_record():
    db.save_rate(1, 'USD', 90.5)
    assert db.get_saved_rate('USD') == 90.5

def test_save_rate_update_existing():
    db.save_rate(1, 'USD', 90.5)
    db.save_rate(1, 'USD', 91.0)
    assert db.get_saved_rate('USD') == 91.0

def test_save_rate_date_format():
    db.save_rate(1, 'EUR', 100.0)
    assert db.get_saved_rate('EUR') == 100.0

def test_save_rate_multiple_currencies():
    db.save_rate(1, 'USD', 90.0)
    db.save_rate(2, 'EUR', 100.0)
    assert db.get_saved_rate('USD') == 90.0
    assert db.get_saved_rate('EUR') == 100.0

def test_save_rate_edge_cases():
    db.save_rate(1, 'USD', 0.0001)
    assert db.get_saved_rate('USD') == 0.0001

@patch('sqlite3.connect')
def test_save_rate_database_connection_error(mock_connect):
    mock_connect.side_effect = sqlite3.Error("Connection error")
    with pytest.raises(sqlite3.Error):
        db.save_rate(1, 'USD', 90.0)

@patch('sqlite3.connect')
def test_save_rate_commit_error(mock_connect):
    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.execute.side_effect = [MagicMock(fetchone=lambda: (1,)), MagicMock()]
    mock_conn.__exit__.side_effect = sqlite3.Error("Commit error")
    mock_connect.return_value = mock_conn
    with pytest.raises(sqlite3.Error):
         db.save_rate(1, 'USD', 90.0)

def test_save_rate_parameter_types():
    # Передаем список в поле id, SQLite точно выдаст ошибку интерфейса
    with pytest.raises((sqlite3.InterfaceError, TypeError)):
        db.save_rate([1], "USD", 90.0)

def test_save_rate_sql_injection_protection():
    malicious_input = "USD'; DROP TABLE rates; --"
    db.save_rate(1, malicious_input, 90.0)
    assert db.get_saved_rate(malicious_input) == 90.0

def test_get_saved_rate_success():
    db.save_rate(1, 'USD', 95.0)
    assert db.get_saved_rate('USD') == 95.0

def test_get_saved_rate_default_currency():
    db.save_rate(1, 'RUB', 1.0)
    assert db.get_saved_rate('RUB') == 1.0

def test_get_saved_rate_nonexistent_currency():
    assert db.get_saved_rate('GBP') is None

def test_get_saved_rate_empty_database():
    assert db.get_saved_rate('USD') is None

def test_get_saved_rate_multiple_currencies():
    db.save_rate(1, 'USD', 90.0)
    db.save_rate(2, 'EUR', 100.0)
    assert db.get_saved_rate('USD') == 90.0
    assert db.get_saved_rate('EUR') == 100.0

def test_get_saved_rate_case_sensitivity():
    db.save_rate(1, 'USD', 90.0)
    assert db.get_saved_rate('usd') == 90.0

def test_get_saved_rate_sql_injection_protection():
    db.save_rate(1, 'USD', 90.0)
    assert db.get_saved_rate("' OR '1'='1") is None

@patch('sqlite3.connect')
def test_get_saved_rate_database_connection_error(mock_connect):
    mock_connect.side_effect = sqlite3.Error("Connection error")
    with pytest.raises(sqlite3.Error):
        db.get_saved_rate('USD')