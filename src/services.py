import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd
import json

from src.utils import filter_transactions_by_date, filter_transaction_by_category_for_cashback

EXCLUDED_CATEGORY = ['Пополнения', 'Переводы', 'Финансы', 'Проценты', 'Бонусы', 'Наличные']

"""Сервисы:
Выгодные категории повышенного кешбэка - DONE
Инвесткопилка
Простой поиск
Поиск по телефонным номерам
Поиск переводов физическим лицам"""

def get_cashback_categories(data: pd.DataFrame, year:int, month:int) -> json:
    """На вход функции поступают данные для анализа, год и месяц. Входные параметры:
    data — данные с транзакциями объектом DataFrame pandas;
    year — год, за который проводится анализ;
    month — месяц, за который проводится анализ.
    На выходе — JSON с анализом, сколько на каждой категории можно заработать кешбэка в указанном месяце года.
    Кэшбек расчитывается как 1% от суммы успешно проведенной операции (оплаты), исключая категории:
    ['Пополнения', 'Переводы', 'Финансы', 'Проценты', 'Бонусы', 'Наличные']
    Данные отсортированы по убыванию по возможной сумме кэшбека"""

    # Создаем переменные для дат в datetime, чтобы фильтровать данные уже имеющейся функцией
    start_date = datetime.datetime(year=year, month=month, day=1)
    end_date = start_date + relativedelta(months=1)

    #Фильтруем транзакции
    filtered_by_date_df = filter_transactions_by_date(df=data, start_date=start_date, end_date=end_date)
    filtered_by_category_df = filter_transaction_by_category_for_cashback(df=filtered_by_date_df, excluded_category=EXCLUDED_CATEGORY)

    # Агрегация по категориям - считаем суммы затрат по каждой категории
    grouped_by_category = filtered_by_category_df.groupby('Категория', as_index=True, sort=True).agg({'Сумма операции':'sum'}).sort_values('Сумма операции')
    cashback_by_categories = grouped_by_category['Сумма операции'].map(lambda value: round(abs(value) / 100, 2))
    result = cashback_by_categories.to_dict()
    return json.dumps(result, ensure_ascii=False)

def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """Функция возвращает сумму, которую удалось бы отложить в «Инвесткопилку».
    принимать на вход три аргумента:
    month — месяц, для которого рассчитывается отложенная сумма (строка в формате 'YYYY-MM').
    transactions — список словарей, содержащий информацию о транзакциях, в которых содержатся следующие поля:
    Дата операции — дата, когда произошла транзакция (строка в формате 'YYYY-MM-DD').
    Сумма операции — сумма транзакции в оригинальной валюте (число).
    limit — предел, до которого нужно округлять суммы операций (целое число).
    """
    pass

