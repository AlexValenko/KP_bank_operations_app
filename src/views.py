import datetime
import json

import pandas as pd
from xmlrpc.client import DateTime

from src.external_api import get_user_rates, get_current_stock_prices_api, get_user_stocks
from src.utils import get_transaction_from_excel, filter_transactions_by_date, get_cards_list_from_data, \
    filter_transactions_by_card, get_total_amount_and_cashback, get_top_transactions


def get_greeting(current_time:DateTime|None=None) -> str:
    """Функция возвращает приветствие в зависимости от времени суток"""
    # Для возможности тестирования в функцию можно передать в качестве аргумента объект DateTime
    if current_time is None:
        current_time = datetime.datetime.now()
    current_hour = int(current_time.hour)
    if current_hour < 6:
        return 'Доброй ночи'
    elif 6 <= current_hour < 12:
        return 'Доброе утро'
    elif 12 <= current_hour < 18:
        return 'Добрый день'
    elif 18 <= current_hour < 24:
        return 'Добрый вечер'

def get_main_page_data(current_date: str, path_excel_file:str='data/operations.xlsx') -> json:

    greeting = get_greeting()

    # Преобразуем полученную строку в объект Datetime, и получаем дату начала месяца
    current_date_dt = datetime.datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S")
    start_date_dt = current_date_dt.replace(day=1, hour=0, minute=0)

    # Чтобы не было проблем с путями и файлами, не указываем путь напрямую, а задаем из главного вызова
    all_transactions_data_df = get_transaction_from_excel(path_xlsx=path_excel_file)
    filtered_by_date_df = filter_transactions_by_date(df=all_transactions_data_df, start_date=start_date_dt, end_date=current_date_dt)
    cards_list = get_cards_list_from_data(df_trsnsactions=filtered_by_date_df)
    top_transactions = get_top_transactions(df=filtered_by_date_df)

    cards_info = []
    for card in cards_list:
        if card not in ['nan', 'NaN', 'NAN', 'Nan'] and card is not None:
            card_transaction_df = filter_transactions_by_card(df=filtered_by_date_df, card_number=card)
            total_amount_and_cashback = get_total_amount_and_cashback(df=card_transaction_df, standard_cashback=True)
            cards_info.append(total_amount_and_cashback)

    currency_rates = get_user_rates()
    tickers = get_user_stocks()
    stock_prices = get_current_stock_prices_api(tickers)

    result = {"greeting": greeting,"cards": cards_info,"top_transactions": top_transactions,"currency_rates" : currency_rates, "stock_prices" : stock_prices}

    return json.dump(result)




    """Для получения требуемого набора данных
(Приветствие в формате  «Доброе утро»  --- функция get_greeting в текущем модуле

По каждой карте:
последние 4 цифры карты; 
общая сумма расходов;
кешбэк (1 рубль на каждые 100 рублей).
Топ-5 транзакций по сумме платежа.
Для этого читаем исходный файл, get_transaction_from_excel
вычисляем даты по которым фильтровать данные
фильтруем его по дате  filter_transactions_by_date

Затем получаем список карт filter_transactions_by_card
Затем в цикле по каждой карте делаем:
filter_transactions_by_card
get_total_amount_and_cashback
get_top_transactions_by_card

Затем 
Курс валют. - get_user_rates из external api
Стоимость акций из S&P500 - get_current_stock_prices_api из external api
Потом собираем все в json."""
