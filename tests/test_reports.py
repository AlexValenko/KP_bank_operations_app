import json

import pytest

from src.reports import spending_by_weekday, spending_by_category, write_down_report_default
from src.utils import get_transaction_from_excel


@pytest.fixture
def get_test_transactions():
    return get_transaction_from_excel('tests/test_data/test_operations.xlsx')

def test_spending_by_weekday(get_test_transactions):
    '''Тестирование функции spending_by_weekday на тестовых данных без задания начальной даты'''
    result_dict = spending_by_weekday(transactions=get_test_transactions).to_dict('records')
    assert result_dict[0].get('День недели') == 'Пятница'
    assert result_dict[0].get('Сумма операции') == -33315.0


def test_spending_by_weekday_only_march(get_test_transactions):
    '''Тестирование функции spending_by_weekday на тестовых данных с заданием начальной даты'''
    result_dict = spending_by_weekday(transactions=get_test_transactions, date='01-04-2026').to_dict('records')
    assert result_dict[0].get('День недели') == 'Понедельник'
    assert result_dict[0].get('Сумма операции') == -31660.1

def test_spending_by_category_success(get_test_transactions) -> None:
    """Проверяет, что расходы по выбранной категории в тестовом файле соответсвуют известному значению"""
    result_dict = spending_by_category(transactions=get_test_transactions, category='Медицина', date='01-06-2026').to_dict('records')
    assert len(result_dict) == 1
    assert result_dict[0]["Сумма платежа"] == -3400.0

def test_spending_by_category_non_category(get_test_transactions, capsys) -> None:
    """Проверяет, что расходы по несуществующей категории не найдены"""
    result_dict = spending_by_category(transactions=get_test_transactions, category='Неизвестная').to_dict('records')
    captured = capsys.readouterr()
    assert len(result_dict) == 0
    assert 'не найдено операций' in captured.out

@write_down_report_default
def single_sum(a, b):
    return a + b

def test_decorator_write_down_report_default_no_dataframe() -> None:
    """Тест декоратора write_down_report_default Если функция возвращает не DataFrame"""
    with pytest.raises(TypeError, match='Функция должна возвращать DataFrame'):
        result = single_sum(2, 3)


def test_decorator_write_down_report_default_success(get_test_transactions) -> None:
    """ПРимер успешной работы декоратора write_down_report_default на примере функции spending_by_weekday на тестовых данных"""
    result_dict = spending_by_weekday(transactions=get_test_transactions, date='01-04-2026').to_dict('records')
    with open('data/default_reports.json', 'r', encoding='utf-8') as file_report:
        report_data = json.load(file_report)
    assert report_data[0] == {
        "День недели": "Понедельник",
        "Сумма операции": -31660.1
    }

def test_decorator_write_down_report_select_file(get_test_transactions, capsys) -> None:
    result_dict = spending_by_category(transactions=get_test_transactions, category='Медицина', date='01-06-2026').to_dict('records')
    captured = capsys.readouterr()
    with open('data/spending_by_category_report.json', 'r', encoding='utf-8') as file_report:
        report_data = json.load(file_report)
    assert report_data[0].get("Категория") == "Медицина"
    assert report_data[0].get("Сумма операции") == -3400.0
    assert 'Результат записан в файл' in captured.out





