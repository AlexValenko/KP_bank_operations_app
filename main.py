from src.reports import spending_by_category, spending_by_weekday
from src.services import get_cashback_categories, investment_bank
from src.utils import get_transaction_from_excel
from src.views import get_main_page_data

if __name__ == "__main__":
    """Основная функциональность программы - выполняет основные функции программы -
    считывает данные из файла XLSX,
    выгружает данные для Веб-страницы 'Главная', формирует из них json-строку,
    Выполняет функции из модулей "Сервисы" и "Отчеты", сохраняет результаты в переменные"""

    # Получение json-строки для Главной страницы
    main_page_data = get_main_page_data(current_date="2026-03-20 12:05:05", path_excel_file="data/operations.xlsx")

    # Сервисы - получение ответов в json
    all_data_transactions = get_transaction_from_excel("data/operations.xlsx")
    # Получение суммы возможного кэшбека по категориям в выбранный месяц. Результат в json-строке
    cashback_by_categories = get_cashback_categories(data=all_data_transactions, year=2026, month=3)
    # Получение суммы, которую удалось бы отложить в «Инвесткопилку» в выбранный месяц. Результат в json-строке
    investments = investment_bank(month="2026-03", transactions=all_data_transactions, limit=50)

    # Отчеты. Функции возвращают DataFrame, декораторы записывают информацию в файлы data/*.json

    # Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)
    current_category_spending = spending_by_category(
        transactions=all_data_transactions, category="Медицина", date="01-05-2026"
    )
    # Функция возвращает средние траты в каждый из дней недели за последние три месяца
    weekdays_spending = spending_by_weekday(transactions=all_data_transactions, date="01-05-2026")
