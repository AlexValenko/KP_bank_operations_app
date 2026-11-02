import json
from unittest.mock import mock_open, patch

import requests

from src.external_api import (
    check_rate_cache,
    get_current_stock_prices_api,
    get_exchange_rate_api,
    get_user_currencies,
    get_user_rates,
    get_user_stocks,
)

# Пример JSON-ответа
MOCK_EXCHANGE_RATE_RESPONSE = {
    "result": "success",
    "documentation": "https://www.exchangerate-api.com/docs",
    "terms_of_use": "https://www.exchangerate-api.com/terms",
    "time_last_update_unix": 1780444801,
    "time_last_update_utc": "Wed, 03 Jun 2026 00:00:01 +0000",
    "time_next_update_unix": 1780531201,
    "time_next_update_utc": "Thu, 04 Jun 2026 00:00:01 +0000",
    "base_code": "RUB",
    "conversion_rates": {"RUB": 1, "USD": 0.01382, "EUR": 0.01183, "CNY": 0.094},
}

USER_CURRENCIES = ["USD", "EUR"]

TEST_RATES_JSON_TODAY = {
    "time_last_update_utc": "Wed, 03 Jun 2026 00:00:01 +0000",
    "conversion_rates": {"USD": 0.01382, "EUR": 0.01183, "RUB": 1},
}

TEST_RATES_JSON_OLD = {
    "time_last_update_utc": "Mon, 01 Jun 2026 00:00:01 +0000",
    "conversion_rates": {"USD": 0.01382, "EUR": 0.01183, "RUB": 1},
}

EXPECTED_RESULT = [{"currency": "USD", "rate": 72.36}, {"currency": "EUR", "rate": 84.53}]

TEST_TICKERS = ["SBER", "GAZP"]

MOCK_STOCKS_RESPONSE = {
    "marketdata": {"data": [["SBER", 250.5, 1.2, 100000], ["GAZP", 150.75, -0.8, 80000], ["LKOH", 6000.0, 2.5, 50000]]}
}

EXPECTED_STOCKS_RESULT = [{"stock": "SBER", "price": 250.5}, {"stock": "GAZP", "price": 150.75}]


def test_get_user_currencies() -> None:
    """Проверяет, что функция get_user_currencies возвращает список и в нем есть значение USD"""
    result = get_user_currencies()
    assert isinstance(result, list)
    assert "USD" in result


def test_get_user_currencies_not_file() -> None:
    """Проверяет, что функция get_user_currencies возвращает список и в нем есть значение USD"""
    result = get_user_currencies(path_settings="missing_file")
    assert result == []


def test_get_user_stocks() -> None:
    """Проверяет, что функция get_user_stocks значения строк"""
    result = get_user_stocks()
    assert isinstance(result, list)


def test_get_user_stocks_not_file() -> None:
    """Проверяет, что функция get_user_stocks значения строк"""
    result = get_user_stocks(path_settings="missing_file")
    assert result == []


def test_get_exchange_rate_api_success() -> None:
    """Тест функции get_exchange_rate_api с подменой запроса и ответа на заранее подготовленный"""
    with (
        patch("os.getenv", return_value="test_api_key_123"),
        patch("requests.get") as mock_get,
        patch("builtins.open", mock_open()) as mock_file,
    ):

        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_EXCHANGE_RATE_RESPONSE

        result = get_exchange_rate_api(base_currency="RUB")

        assert result is None

        expected_url = "https://v6.exchangerate-api.com/v6/test_api_key_123/latest/RUB"
        mock_get.assert_called_once_with(url=expected_url, timeout=10)

        mock_file.assert_called_with("data/rates.json", "w")

        handle = mock_file()

        # Собираем все записанные данные в одну строку
        written_data = "".join(call_args[0][0] for call_args in handle.write.call_args_list)

        # Парсим JSON
        parsed_written_data = json.loads(written_data)

        assert parsed_written_data == MOCK_EXCHANGE_RATE_RESPONSE


def test_check_rate_cache_file_exists_today():
    """Проверяет, если файл существует, дата сегодня — возвращает True. Дата не совпадает, должно быть False"""
    with (
        patch("os.path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data=json.dumps(TEST_RATES_JSON_TODAY))) as mock_file,
    ):

        result = check_rate_cache("data/rates.json")

        assert result is False
        mock_file.assert_called_with("data/rates.json", "r", encoding="utf-8")


def test_check_rate_cache_file_exists_old_date():
    """Проверяет, файл существует, но дата старая — возвращает False"""
    with (
        patch("os.path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data=json.dumps(TEST_RATES_JSON_OLD))) as mock_file,
    ):

        result = check_rate_cache("data/rates.json")

        assert result is False
        mock_file.assert_called_with("data/rates.json", "r", encoding="utf-8")


def test_check_rate_cache_file_not_exists():
    """Проверяет, если файла нет — возвращает False и печатает сообщение"""
    with patch("os.path.exists", return_value=False), patch("builtins.print") as mock_print:

        result = check_rate_cache("data/rates.json")

        assert result is False
        mock_print.assert_called_with("File not found")


def test_get_user_rates_with_valid_cache():
    """Тест функции get_user_rates с использованием кэша для расчёта курсов"""
    with (
        patch("src.external_api.get_user_currencies", return_value=USER_CURRENCIES),
        patch("src.external_api.check_rate_cache", return_value=True),
        patch("builtins.open", mock_open(read_data=json.dumps(TEST_RATES_JSON_TODAY))) as mock_file,
        patch("builtins.print") as mock_print,
    ):

        result = get_user_rates()

        assert result == EXPECTED_RESULT

        # Проверяем, что check_rate_cache был вызван
        mock_print.assert_any_call("Используем актуальный кэш")

        # Проверяем открытие файла
        mock_file.assert_called_with("data/rates.json", "r", encoding="utf-8")


def test_get_current_stock_prices_api_success():
    """Тест успешного получения цен акций с Мосбиржи"""
    with (
        patch("requests.get") as mock_get,
        patch("builtins.open", mock_open()) as mock_file,
        patch("os.makedirs") as mock_makedirs,
    ):

        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_STOCKS_RESPONSE

        result = get_current_stock_prices_api(TEST_TICKERS)
        assert result == EXPECTED_STOCKS_RESULT

        expected_params = {
            "iss.meta": "off",
            "iss.only": "securities,marketdata",
            "securities.columns": "SECID,SHORTNAME",
            "marketdata.columns": "SECID,LAST,CHANGE,VALTODAY",
        }
        mock_get.assert_called_once_with(
            "https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json",
            params=expected_params,
            timeout=10,
        )

        # Проверка создания директории
        mock_makedirs.assert_called_with("data", exist_ok=True)

        # Проверка открытия файла для записи
        mock_file.assert_called_with("data/stocks.json", "w", encoding="utf-8")


def test_get_current_stock_prices_api_network_error():
    """Тест обработки сетевой ошибки при получении цен акций"""
    with (
        patch("requests.get", side_effect=requests.exceptions.RequestException("Connection failed")),
        patch("builtins.print") as mock_print,
    ):

        result = get_current_stock_prices_api(TEST_TICKERS)

        assert result is None

        # Проверка вывода сообщения об ошибке
        mock_print.assert_called_with("Network error Connection failed")
