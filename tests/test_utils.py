import datetime

import pytest

from src.utils import (
    filter_transactions_by_card,
    filter_transactions_by_date,
    get_cards_list_from_data,
    get_top_transactions,
    get_total_amount_and_cashback,
    get_transaction_from_excel,
)

""" Для тестов используется файл tests/test_data/test_operations.xlsx.
В нем операции с 02.03.2026 по 03.04.2026, есть пропущенные данные и статус FAILED
Срезки по этому файлу представлены в константах и фикстурах
"""


def test_get_transaction_from_excel_normal() -> None:
    """Пример нормальной работы функции get_transaction_from_excel
    с тестовым файлом tests_data/transactions_test_excel.xlsx
    Проверка на сумму столбца "Сумма операций - числа читаются нормально, не как строки"""
    result = get_transaction_from_excel(path_xlsx="tests/test_data/test_operations.xlsx")
    sum_operations = result["Сумма операции"].sum()
    assert sum_operations == -63325.84


def test_get_transaction_from_excel_not_file(capsys: pytest.CaptureFixture[str]) -> None:
    """Пример работы функции get_transaction_from_excel если файл не найден"""
    result = get_transaction_from_excel(path_xlsx="tests/test_data/not_file.xlsx")
    captured = capsys.readouterr()
    assert captured.out == "File not found\n"
    assert result is None


def test_get_transaction_from_excel_missing_columns() -> None:
    """Тест функции get_transaction_from_excel при отсутствии обязательных столбцов в файле"""
    # Проверяем, что функция выбрасывает ValueError при отсутствующих столбцах
    with pytest.raises(ValueError) as exc_info:
        get_transaction_from_excel(path_xlsx="tests/test_data/invalid_file.xlsx")

    assert "Отсутствует один или несколько обязательных столбцов" in str(exc_info.value)


def test_get_cards_list_from_data() -> None:
    """Тестирование на корректную агрегацию карт в тестовом файле, 3 значение nan"""
    test_df = get_transaction_from_excel(path_xlsx="tests/test_data/test_operations.xlsx")
    result = get_cards_list_from_data(df_trsnsactions=test_df)
    assert "*3753" in result
    assert "*2822" in result
    assert len(result) == 3


def test_filter_transactions_by_date_success() -> None:
    """Проверяет фильтр по дате операций. За выбранный период сравнивается сумма операций с заранее известной"""
    test_df = get_transaction_from_excel(path_xlsx="tests/test_data/test_operations.xlsx")
    start_date_test = datetime.datetime(year=2026, month=4, day=1)
    end_date_test = datetime.datetime(year=2026, month=5, day=1)
    filtered_df_in_april = filter_transactions_by_date(df=test_df, start_date=start_date_test, end_date=end_date_test)
    sum_operations_april = filtered_df_in_april["Сумма операции"].sum()
    filtered_df_all_time = filter_transactions_by_date(df=test_df)
    sum_operations_total = filtered_df_all_time["Сумма операции"].sum()
    assert sum_operations_april == -16997.36
    # Также проверим, что если вызывать функцию без аргументов, то выведет все операции с 2000 года до сегодня
    assert sum_operations_total == -63325.84


def test_filter_transactions_by_card_success() -> None:
    """Проверяем, что сумма операций по карте *2822 в тестовом файле соответствует известному значению"""
    test_df = get_transaction_from_excel(path_xlsx="tests/test_data/test_operations.xlsx")
    current_card_transactions = filter_transactions_by_card(df=test_df, card_number="*2822")
    sum_operations_card = current_card_transactions["Сумма операции"].sum()
    assert sum_operations_card == -21662.60


def test_get_total_amount_and_cashback_standard() -> None:
    """Пример нормальной работы get_total_amount_and_cashback с расчетом кэшбека 1%"""
    test_df = get_transaction_from_excel(path_xlsx="tests/test_data/test_operations.xlsx")
    current_card_transactions = filter_transactions_by_card(df=test_df, card_number="*2822")
    result_standard = get_total_amount_and_cashback(df=current_card_transactions)
    assert result_standard == {"last_digits": "*2822", "total_spent": 22419.0, "cashback": 224.19}


def test_get_total_amount_and_cashback_real() -> None:
    """Пример работы get_total_amount_and_cashback с кешбэком из реальных значений"""
    test_df = get_transaction_from_excel(path_xlsx="tests/test_data/test_operations.xlsx")
    current_card_transactions = filter_transactions_by_card(df=test_df, card_number="*2822")
    result_standard = get_total_amount_and_cashback(df=current_card_transactions, standard_cashback=False)
    assert result_standard == {"last_digits": "*2822", "total_spent": 22419.0, "cashback": 0.0}


def test_get_total_amount_and_cashback_incorrect() -> None:
    """Пример работы get_total_amount_and_cashback если на входе данные по многим картам"""
    test_df = get_transaction_from_excel(path_xlsx="tests/test_data/test_operations.xlsx")
    result_standard = get_total_amount_and_cashback(df=test_df)
    assert result_standard == {}


def test_get_top_transactions() -> None:
    test_df = get_transaction_from_excel(path_xlsx="tests/test_data/test_operations.xlsx")
    current_card_transactions = filter_transactions_by_card(df=test_df, card_number="*2822")
    top_transactions_2822 = get_top_transactions(df=current_card_transactions)
    # Проверяем, что максимальный расход по выбранной карте соответствует значению из тестового файла
    assert top_transactions_2822[0]["amount"] == -22419.00
    assert len(top_transactions_2822) == 5
    assert isinstance(top_transactions_2822, list)
