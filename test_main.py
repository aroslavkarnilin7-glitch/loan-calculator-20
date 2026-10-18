import pytest
from unittest.mock import patch, MagicMock
import main

@pytest.fixture
def app():
    app = main.CurrencyConverterApp()
    app.withdraw()
    yield app
    app.destroy()

def test_calculate_loan_success(app):
    app.loan_var.set("100000")
    app.loan_time_var.set("12")
    app.annual_interest_var.set("10")
    app.calculate_loan()
    assert "Ежемесячный платёж:" in app.monthly_label.cget("text")
    assert app.monthly_payment is not None

def test_calculate_loan_invalid_loan_amount(app):
    app.loan_var.set("-100")
    app.calculate_loan()
    log_text = app.log_text.get("1.0", "end")
    assert "Сумма кредита должна быть больше 0" in log_text

def test_convert_success(app):
    app.monthly_payment = 10000
    app.target_var.set("USD")
    with patch('db.get_saved_rate', return_value=90.0):
        app.convert()
        assert "10000.00 RUB" in app.result_label.cget("text")

def test_convert_none_rate(app):
    app.monthly_payment = 10000
    app.target_var.set("USD")
    with patch('db.get_saved_rate', return_value=None):
        app.convert()
        log_text = app.log_text.get("1.0", "end")
        assert "не найден" in log_text

@patch('main.api.fetch_rates')
def test_convert_exception(mock_fetch, app):
    app.monthly_payment = 10000
    app.target_var.set("USD")
    with patch('db.get_saved_rate', side_effect=Exception("DB error")):
        app.convert()

@patch('main.api.fetch_rates')
@patch('main.db.save_rate')
def test_update_db_success(mock_save, mock_fetch, app):
    mock_fetch.return_value = {"Valute": {"USD": {"Value": 90.0, "Nominal": 1}}}
    app.update_db()
    log_text = app.log_text.get("1.0", "end")
    assert "Курсы обновлены" in log_text

@patch('main.api.fetch_rates')
def test_update_db_empty_rates(mock_fetch, app):
    mock_fetch.return_value = {"Valute": {}}
    app.update_db()
    log_text = app.log_text.get("1.0", "end")
    assert "API не вернул данные" in log_text