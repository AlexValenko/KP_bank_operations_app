import datetime
import pytest

from src.services import get_cashback_categories
from src.utils import get_transaction_from_excel


def test_get_cashback_categories() -> None:
    all_data_transactions = get_transaction_from_excel('tests/test_data/test_operations.xlsx')
    result = get_cashback_categories(data=all_data_transactions, year=2026, month=4)
    assert result == '{"Медицина": 34.0, "Супермаркеты": 4.91}'
