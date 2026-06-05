import datetime
from typing import Optional

from dateutil.relativedelta import relativedelta

import pandas as pd
import json

from src.utils import filter_transactions_by_date

WEEKDAYS = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

def spending_by_category(transactions: pd.DataFrame,
                         category: str="",
                         date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)."""

    # Создаем переменные для дат в datetime, чтобы фильтровать данные уже имеющейся функцией
    if date is None:
        end_date = datetime.datetime.today()
    else:
        end_date = datetime.datetime.strptime(date, "%d-%m-%Y")
    start_date = end_date - relativedelta(months=3)

    filtered_by_date_df = filter_transactions_by_date(df=transactions, start_date=start_date,
                                                      end_date=end_date)

    # Фильтруем данные, чтобы остались только расходы (сумма операции < 0), статус - ОК, валюта - руб, категория есть
    cleaned_for_calc_df = filtered_by_date_df[
        (filtered_by_date_df['Статус'] == "OK") &
        (filtered_by_date_df['Категория'].notna()) &
        (filtered_by_date_df['Сумма операции'] < 0) &
        (filtered_by_date_df['Валюта платежа'] == "RUB")]

    grouped_by_category = cleaned_for_calc_df.groupby('Категория', as_index=True, sort=True, group_keys=True, observed=True).agg({'Сумма операции': 'sum'})

    if category in grouped_by_category.index:
        filtered_by_currency_category = cleaned_for_calc_df[cleaned_for_calc_df['Категория'] == category]
        print(f'Найдено {len(filtered_by_currency_category)} операций по категории {category}')
        return filtered_by_currency_category
    else:
        print(f'По категории {category} не найдено операций')
        return pd.DataFrame()


def spending_by_weekday(transactions: pd.DataFrame,
                        date: Optional[str] = None) -> pd.DataFrame:
    '''Функция принимает на вход:
    датафрейм с транзакциями,
    опциональную дату (Если дата не передана, то берется текущая дата)
    Функция возвращает средние траты в каждый из дней недели за последние три месяца (от переданной даты).'''

    # Получение объекта datetime из входящей строки
    if date is None:
        end_date = datetime.datetime.today()
    else:
        end_date = datetime.datetime.strptime(date, "%d-%m-%Y")
    start_date = end_date - relativedelta(months=3)

    filtered_by_date_df = filter_transactions_by_date(df=transactions, start_date=start_date,
                                                      end_date=end_date)
    # Чистим данные, чтобы остались только расходы
    cleaned_for_calc_df = filtered_by_date_df[
        (filtered_by_date_df['Статус'] == "OK") &
        (filtered_by_date_df['Сумма операции'] < 0) &
        (filtered_by_date_df['Валюта платежа'] == "RUB")]

    cleaned_for_calc_df['День недели'] = cleaned_for_calc_df['Дата операции'].map(lambda x: WEEKDAYS[x.weekday()])
    grouped_by_weekday_df = cleaned_for_calc_df.groupby(by='День недели', as_index=True, group_keys=True).agg({'Сумма операции' : 'sum'}).sort_values('Сумма операции')
    return grouped_by_weekday_df



