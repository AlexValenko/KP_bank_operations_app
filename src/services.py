import datetime
import json
import logging

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.utils import filter_transaction_by_category_for_cashback, filter_transactions_by_date

EXCLUDED_CATEGORY = ["Пополнения", "Переводы", "Финансы", "Проценты", "Бонусы", "Наличные"]

services_logger = logging.getLogger("services")
file_handler = logging.FileHandler("logs/log_services.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
services_logger.addHandler(file_handler)
services_logger.setLevel(logging.DEBUG)


def get_cashback_categories(data: pd.DataFrame, year: int, month: int) -> json:
    """На вход функции поступают данные для анализа, год и месяц. Входные параметры:
    data — данные с транзакциями объектом DataFrame pandas;
    year — год, за который проводится анализ;
    month — месяц, за который проводится анализ.
    На выходе — JSON с анализом, сколько на каждой категории можно заработать кешбэка в указанном месяце года.
    Кэшбек расчитывается как 1% от суммы успешно проведенной операции (оплаты), исключая категории:
    ['Пополнения', 'Переводы', 'Финансы', 'Проценты', 'Бонусы', 'Наличные']
    Данные отсортированы по убыванию по возможной сумме кэшбека"""

    # Создаем переменные для дат в datetime, чтобы фильтровать данные уже имеющейся функцией
    try:
        start_date = datetime.datetime(year=year, month=month, day=1)
        end_date = start_date + relativedelta(months=1)
        services_logger.debug(f"Выбран месяц {month} {year} года")
    except (TypeError, ValueError) as e:
        services_logger.error(f"Ошибка {e} чтения даты из аргументов функции, требуется YYYY - int, MM - int(1-12)")
        return None

    # Фильтруем транзакции
    filtered_by_date_df = filter_transactions_by_date(df=data, start_date=start_date, end_date=end_date)
    services_logger.debug(f"Транзакции отфильтрованы по дате, выбрано {len(filtered_by_date_df)} записей")
    filtered_by_category_df = filter_transaction_by_category_for_cashback(
        df=filtered_by_date_df, excluded_category=EXCLUDED_CATEGORY
    )

    if filtered_by_category_df.empty:
        services_logger.warning("Не найдено подходящих транзакций для начисления кэшбэка")
        print("Не найдено подходящих транзакций для начисления кэшбэка")
        return None
    services_logger.debug(
        f"Транзакции отфильтрованы статусу и категории, выбрано {len(filtered_by_category_df)} записей"
    )

    # Агрегация по категориям - считаем суммы затрат по каждой категории
    grouped_by_category = (
        filtered_by_category_df.groupby("Категория", as_index=True, sort=True)
        .agg({"Сумма операции": "sum"})
        .sort_values("Сумма операции")
    )
    cashback_by_categories = grouped_by_category["Сумма операции"].map(lambda value: round(abs(value) / 100, 2))
    services_logger.debug("Транзакции сгруппированы по категориям, вычислен расчетный кэшбэк \n")
    result = cashback_by_categories.to_dict()
    return json.dumps(result, ensure_ascii=False)


def investment_bank(month: str, transactions: pd.DataFrame, limit: int = 50) -> float:
    """Функция возвращает сумму, которую удалось бы отложить в «Инвесткопилку».
    Принимает на вход три аргумента:
    month — месяц, для которого рассчитывается отложенная сумма (строка в формате 'YYYY-MM').
    transactions — DataFrame pandas с банковскими операциями.
    Сумма операции — сумма транзакции в оригинальной валюте (число).
    limit — предел, до которого нужно округлять суммы операций (целое число), по умолчанию - 50 руб.
    """
    # Получение объекта datetime из входящей строки
    try:
        start_current_month = datetime.datetime.strptime(month, "%Y-%m")
    except (TypeError, ValueError) as e:
        services_logger.error(f"Ошибка {e} чтения даты из аргументов функции, строка в формате 'YYYY-MM'")
        return 0.00
    end_current_month = start_current_month + relativedelta(months=1)
    services_logger.debug(f"Выбран период за {start_current_month.month} месяц {start_current_month.year} года")

    # Фильтруем транзакции по дате за выбранный месяц
    filtered_by_date_df = filter_transactions_by_date(
        df=transactions, start_date=start_current_month, end_date=end_current_month
    )
    services_logger.debug(f"Транзакции отфильтрованы по дате, выбрано {len(filtered_by_date_df)} записей")

    # Фильтруем транзакции, оставляя только покупки исключая категории:
    # ['Пополнения', 'Переводы', 'Проценты', 'Бонусы', 'Наличные']
    investment_bank_df = filter_transaction_by_category_for_cashback(
        df=filtered_by_date_df, excluded_category=["Пополнения", "Переводы", "Проценты", "Бонусы", "Наличные"]
    )
    if investment_bank_df.empty:
        services_logger.warning("Не найдено подходящих транзакций для вычисления округлений по операциям")
        print("Не найдено подходящих транзакций для вычисления округлений по операциям")
        return 0.00
    services_logger.debug(f"Транзакции отфильтрованы статусу и категории, выбрано {len(investment_bank_df)} записей")
    # Добавляем в таблицу новое поле "Округление"
    investment_bank_df["Округление"] = abs(investment_bank_df["Сумма операции"]).map(
        lambda x: 0.0 if (x % limit) == 0 else limit - (x % limit)
    )
    result = round(investment_bank_df["Округление"].sum(), 2)
    services_logger.debug(f"Функция успешно выполнена, сумма инвесткопилки за выбранный период {result} \n")
    return result
