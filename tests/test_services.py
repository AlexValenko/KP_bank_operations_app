import datetime
import pytest

from src.services import get_cashback_categories, investment_bank
from src.utils import get_transaction_from_excel

@pytest.fixture
def get_test_transactions():
    return get_transaction_from_excel('tests/test_data/test_operations.xlsx')

def test_get_cashback_categories(get_test_transactions) -> None:
    """Тестирование функции get_cashback_categories на заранее подготовленных данных test_operations.xlsx"""
    result = get_cashback_categories(data=get_test_transactions, year=2026, month=4)
    assert result == '{"Медицина": 34.0, "Супермаркеты": 4.91}'

def test_get_cashback_categories_invalid_args(get_test_transactions) -> None:
    """Тестирование функции get_cashback_categories c некорректно заданной датой"""
    result = get_cashback_categories(data=get_test_transactions, year=2026, month=18)
    assert result is None

def test_get_cashback_categories_not_transactions(get_test_transactions, capsys) -> None:
    """Тестирование функции get_cashback_categories если не найдено транзакций"""
    result = get_cashback_categories(data=get_test_transactions, year=2026, month=2)
    captured = capsys.readouterr()
    assert result is None
    assert 'Не найдено подходящих транзакций' in captured.out

def test_investment_bank_april_2026(get_test_transactions):
    """Тестирование функции investment_bank на заранее подготовленных данных test_operations.xlsx за апрель 2026"""
    result = investment_bank(month='2026-04', transactions=get_test_transactions, limit=50)
    assert result == 9.32

def test_investment_bank_march_2026(get_test_transactions):
    """Тестирование функции investment_bank на заранее подготовленных данных test_operations.xlsx за март 2026"""
    result = investment_bank(month='2026-03', transactions=get_test_transactions, limit=50)
    assert result == 49.08

def test_investment_bank_incorrect_args(get_test_transactions):
    """Тестирование функции investment_bank с некорректной датой на входе"""
    result = investment_bank(month='2026-15-03', transactions=get_test_transactions, limit=50)
    assert result == 0.00

def test_investment_bank_feb_2026(get_test_transactions, capsys):
    """Тестирование функции investment_bank на заранее подготовленных данных test_operations.xlsx за февраль 2026"""
    result = investment_bank(month='2026-02', transactions=get_test_transactions, limit=50)
    captured = capsys.readouterr()
    assert result == 0.00
    assert 'Не найдено подходящих транзакций' in captured.out
