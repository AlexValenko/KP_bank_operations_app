import datetime
import json
from xmlrpc.client import DateTime
import logging
import pandas as pd

from src.external_api import get_current_stock_prices_api, get_user_rates, get_user_stocks
from src.utils import (
    filter_transactions_by_card,
    filter_transactions_by_date,
    get_cards_list_from_data,
    get_top_transactions,
    get_total_amount_and_cashback,
    get_transaction_from_excel,
)

views_logger = logging.getLogger('logger_views')
file_handler = logging.FileHandler('logs/log_views.log', mode='w', encoding='utf-8')
file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
file_handler.setFormatter(file_formatter)
views_logger.addHandler(file_handler)
views_logger.setLevel(logging.DEBUG)

def get_greeting(current_time: DateTime | None = None) -> str:
    """Функция возвращает приветствие в зависимости от времени суток"""
    # Для возможности тестирования в функцию можно передать в качестве аргумента объект DateTime
    if current_time is None:
        current_time = datetime.datetime.now()
    current_hour = int(current_time.hour)
    if current_hour < 6:
        return "Доброй ночи"
    elif 6 <= current_hour < 12:
        return "Доброе утро"
    elif 12 <= current_hour < 18:
        return "Добрый день"
    elif 18 <= current_hour < 24:
        return "Добрый вечер"


def get_main_page_data(current_date: str, path_excel_file: str = "data/operations.xlsx") -> json:
    """Основная функция для получения данных для главной страницы,
    принимает на вход дату в строковом формате YYYY-MM-DD HH:MM:SS и возвращает JSON-ответ со следующими данными:
    Приветствие в формате «Доброе утро» / «Добрый день» в зависимости от текущего времени.
    По каждой карте:
    последние 4 цифры карты;
    общая сумма расходов;
    кешбэк (1 рубль на каждые 100 рублей).
    Топ-5 транзакций по сумме платежа.
    Курс заданных в пользовательских настройках валют из exchangerate-api.
    Стоимость заданных в пользовательских настройках акций из Мосбиржи.
    Упаковывает данные в JSON строку"""

    greeting = get_greeting()
    views_logger.debug("Получено приветствие")

    # Преобразуем полученную строку в объект Datetime, и получаем дату начала месяца
    current_date_dt = datetime.datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S")
    start_date_dt = current_date_dt.replace(day=1, hour=0, minute=0)
    views_logger.debug(f"Выбран временной диапазон с {start_date_dt.strftime(format='%d-%m-%Y')} по {current_date_dt.strftime(format='%d-%m-%Y')}")


    # Чтобы не было проблем с путями и файлами, не указываем путь напрямую, а задаем из главного вызова
    all_transactions_data_df = get_transaction_from_excel(path_xlsx=path_excel_file)
    views_logger.info(f'Файл {path_excel_file} успешно загружен, количество строк {len(all_transactions_data_df)}')

    filtered_by_date_df = filter_transactions_by_date(
        df=all_transactions_data_df, start_date=start_date_dt, end_date=current_date_dt
    )
    views_logger.debug(f'В выбранном временном диапазоне {len(filtered_by_date_df)} транзакций')
    cards_list = get_cards_list_from_data(df_trsnsactions=filtered_by_date_df)
    views_logger.debug('Получен список банковских карт...')

    top_transactions = get_top_transactions(df=filtered_by_date_df)
    views_logger.debug(f'Получено {len(top_transactions)} Топ-транзакций')

    cards_info = []
    for card in cards_list:
        if card is None:
            continue
        if isinstance(card, str) and card.strip() == '':
            continue
        if pd.isna(card):
            continue
        if isinstance(card, str) and card.lower() == 'nan':
            continue
        card_transaction_df = filter_transactions_by_card(df=filtered_by_date_df, card_number=card)
        total_amount_and_cashback = get_total_amount_and_cashback(df=card_transaction_df, standard_cashback=True)
        cards_info.append(total_amount_and_cashback)
    views_logger.debug(f'Данные по банковским картам получены, количество карт: {len(cards_info)}')

    currency_rates = get_user_rates()
    if currency_rates == []:
        views_logger.error('Ошибка получения курсов валют в модуле external_api.')
    else:
        views_logger.debug('Данные по курсам выбранных валют получены, актуальные данные в data/rates.json')

    tickers = get_user_stocks()
    stock_prices = get_current_stock_prices_api(tickers)
    if stock_prices is None:
        views_logger.error('Ошибка получения стоимости акций в модуле external_api.')
        stock_prices = []
    else:
        views_logger.debug('Данные по стоимости выбранных акций получены')

    result = {
        "greeting": greeting,
        "cards": cards_info,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    views_logger.debug('Ответ сформирован в JSON')


    return json.dumps(result, ensure_ascii=False)
