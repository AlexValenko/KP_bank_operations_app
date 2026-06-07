import datetime
import json
from unittest.mock import patch

from src.views import get_greeting, get_main_page_data


def test_get_greeting_morning() -> None:
    test_time = datetime.datetime(2023, 1, 1, 6, 0, 0)  # 6:00
    result = get_greeting(test_time)
    assert result == "Доброе утро"


def test_get_greeting_noon() -> None:
    test_time = datetime.datetime(2023, 1, 1, 12, 1, 5)  # 12:01
    result = get_greeting(test_time)
    assert result == "Добрый день"


def test_get_greeting_evening() -> None:
    test_time = datetime.datetime(2023, 1, 1, 18, 1, 5)  # 18:01
    result = get_greeting(test_time)
    assert result == "Добрый вечер"


def test_get_greeting_night() -> None:
    test_time = datetime.datetime(2023, 1, 1, 0, 0, 0)  # 0:00
    result = get_greeting(test_time)
    assert result == "Доброй ночи"


def test_get_main_page_data() -> None:
    """Проверка работы основной логики функции, если не получены данные по API"""
    with (
        patch("src.views.get_user_rates", return_value=[]),
        patch("src.views.get_user_stocks", return_value=[]),
        patch("src.views.get_greeting", return_value="Доброе утро"),
    ):
        result = get_main_page_data(
            current_date="2026-03-20 12:00:02", path_excel_file="tests/test_data/test_operations.xlsx"
        )

        # Парсим JSON-строку в словарь для сравнения
        parsed_result = json.loads(result)

        # Проверяем приветствие
        assert parsed_result["greeting"] == "Доброе утро"

        # Проверяем данные по картам
        assert "cards" in parsed_result
        assert len(parsed_result["cards"]) == 2
        assert parsed_result["cards"][0]["last_digits"] == "*3753"
        assert abs(parsed_result["cards"][0]["total_spent"] - 31859.1) < 0.01  # Учитываем погрешность float
        assert abs(parsed_result["cards"][0]["cashback"] - 318.59) < 0.01
        assert parsed_result["cards"][1]["last_digits"] == "*2822"
        assert abs(parsed_result["cards"][1]["total_spent"] - 22419.0) < 0.01
        assert abs(parsed_result["cards"][1]["cashback"] - 224.19) < 0.01

        # Проверяем топ‑транзакции
        assert "top_transactions" in parsed_result
        assert len(parsed_result["top_transactions"]) == 5
        assert parsed_result["top_transactions"][0]["date"] == "02-03-2026"
        assert parsed_result["top_transactions"][0]["amount"] == -27000.0
        assert parsed_result["top_transactions"][0]["category"] == "Переводы"
        assert parsed_result["top_transactions"][0]["description"] == "Александр В."

        # Проверяем пустые данные по API
        assert parsed_result["currency_rates"] == []
        assert parsed_result["stock_prices"] == []
