import pytest

from src.reports import spending_by_weekday
from src.utils import get_transaction_from_excel


@pytest.fixture
def get_test_transactions():
    return get_transaction_from_excel('tests/test_data/test_operations.xlsx')

def test_spending_by_weekday(get_test_transactions):
    '''Тестирование функции spending_by_weekday на тестовых данных без задания начальной даты'''
    result_dict = spending_by_weekday(transactions=get_test_transactions).to_dict()
    assert result_dict.get('Сумма операции').get('Пятница') == -33315.0


def test_spending_by_weekday_only_march(get_test_transactions):
    '''Тестирование функции spending_by_weekday на тестовых данных с заданием начальной даты'''
    result_dict = spending_by_weekday(transactions=get_test_transactions, date='01-04-2026').to_dict()
    assert result_dict.get('Сумма операции').get('Пятница') == -30099.0

