import pytest

"""Для тестов используется файл tests/test_data/test_operations.xlsx. 
В нем операции с 02.03.2026 по 03.04.2026, есть пропущенные данные и статус FAILED
Срезки по этому файлу представлены в константах и фикстурах
"""

def test_get_transaction_from_excel_normal(first_transactions: list) -> None:
    """Пример нормальной работы функции get_transaction_from_excel
    с тестовым файлом tests_data/transactions_test_excel.xlsx"""
    result = get_transaction_from_excel(path_xlsx="tests/tests_data/transactions_test_excel.xlsx")
    assert result == first_transactions
    assert isinstance(result, list)
