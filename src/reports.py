import datetime
import json
import logging
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.utils import filter_transactions_by_date

WEEKDAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

reports_logger = logging.getLogger("reports")
file_handler = logging.FileHandler("logs/log_reports.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
reports_logger.addHandler(file_handler)
reports_logger.setLevel(logging.DEBUG)


def write_down_report_default(func: callable) -> None:
    """Декоратор, записывает DataFrame в словарь и сохраняет его в файле data/default_reports.json"""

    def wrapper(*args, **kwargs):
        reports_logger.debug("Вызван декоратор write_down_report_default")
        result = func(*args, **kwargs)
        if not isinstance(result, pd.DataFrame):
            reports_logger.error("Декорируемая функция должна возвращать DataFrame")
            raise TypeError("Функция должна возвращать DataFrame")

        for col in result.columns:
            if pd.api.types.is_datetime64_any_dtype(result[col]):
                result[col] = result[col].dt.strftime("%Y-%m-%d %H:%M:%S")
        reports_logger.debug("Даты из DataFrame преобразованы в str для парсинга ...")

        result_dict = result.to_dict("records")
        try:
            with open("data/default_reports.json", "w", encoding="utf-8") as file_report:
                json.dump(result_dict, file_report, indent=4, ensure_ascii=False)
                reports_logger.debug("Файл data/default_reports.json успешно записан \n")
        except Exception as e:
            print(f"Ошибка при сохранении отчета: {e}")
            reports_logger.error(f"Ошибка при сохранении отчета: {e}")

        return result

    return wrapper


def write_down_report_select_file(file_path):
    """Декоратор, записывает DataFrame в словарь и сохраняет его в файл,
    путь к которому передан в аргумент декоратора"""

    def wrapper(func: callable):
        def inner(*args, **kwargs):
            reports_logger.debug("Вызван декоратор write_down_report_select_file")
            result = func(*args, **kwargs)
            if not isinstance(result, pd.DataFrame):
                reports_logger.error("Декорируемая функция должна возвращать DataFrame")
                raise TypeError("Функция должна возвращать DataFrame")

            for col in result.columns:
                if pd.api.types.is_datetime64_any_dtype(result[col]):
                    result[col] = result[col].dt.strftime("%Y-%m-%d %H:%M:%S")
            reports_logger.debug("Даты из DataFrame преобразованы в str для парсинга ...")

            result_dict = result.to_dict("records")

            try:
                with open(file_path, "w", encoding="utf-8") as file_report:
                    json.dump(result_dict, file_report, indent=4, ensure_ascii=False)
                    reports_logger.debug(f"Результат успешно записан в файл {file_path} \n")
            except Exception as e:
                print(f"Ошибка при сохранении отчета: {e}")
                reports_logger.error(f"Ошибка при сохранении отчета: {e}")
            return result

        return inner

    return wrapper


@write_down_report_select_file(file_path="data/spending_by_category_report.json")
def spending_by_category(transactions: pd.DataFrame, category: str = "", date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)."""

    # Создаем переменные для дат в datetime, чтобы фильтровать данные уже имеющейся функцией
    if date is None:
        end_date = datetime.datetime.today()
    else:
        try:
            end_date = datetime.datetime.strptime(date, "%d-%m-%Y")
        except (TypeError, ValueError) as e:
            reports_logger.error(f"Ошибка {e} чтения даты из аргументов функции, требуется dd-mm-YYYY")
            return pd.DataFrame()
    start_date = end_date - relativedelta(months=3)
    reports_logger.debug(
        f'Выбран диапазон дат с {start_date.strftime("%d-%m-%Y")}  по {end_date.strftime("%d-%m-%Y")}'
    )

    filtered_by_date_df = filter_transactions_by_date(df=transactions, start_date=start_date, end_date=end_date)
    reports_logger.debug(f"Транзакции отфильтрованы по дате, выбрано {len(filtered_by_date_df)} записей")

    # Фильтруем данные, чтобы остались только расходы (сумма операции < 0), статус - ОК, валюта - руб, категория есть
    cleaned_for_calc_df = filtered_by_date_df[
        (filtered_by_date_df["Статус"] == "OK")
        & (filtered_by_date_df["Категория"].notna())
        & (filtered_by_date_df["Сумма операции"] < 0)
        & (filtered_by_date_df["Валюта платежа"] == "RUB")
    ]

    if cleaned_for_calc_df.empty:
        reports_logger.warning("Не найдено подходящих транзакций")
        return pd.DataFrame()
    reports_logger.debug(f"Транзакции отфильтрованы статусу и категории, выбрано {len(cleaned_for_calc_df)} записей")

    grouped_by_category = cleaned_for_calc_df.groupby(
        "Категория", as_index=True, sort=True, group_keys=True, observed=True
    ).agg({"Сумма операции": "sum"})
    reports_logger.debug(f"Транзакции сгруппированы по {len(grouped_by_category)} категориям")

    if category in grouped_by_category.index:
        filtered_by_currency_category = cleaned_for_calc_df[cleaned_for_calc_df["Категория"] == category]
        reports_logger.debug(f"Найдено {len(filtered_by_currency_category)} операций по категории {category}")
        return filtered_by_currency_category
    else:
        reports_logger.warning(f"По категории {category} не найдено операций")
        return pd.DataFrame()


@write_down_report_default
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Функция принимает на вход:
    датафрейм с транзакциями,
    опциональную дату (Если дата не передана, то берется текущая дата)
    Функция возвращает средние траты в каждый из дней недели за последние три месяца (от переданной даты)."""

    # Получение объекта datetime из входящей строки
    if date is None:
        end_date = datetime.datetime.today()
    else:
        try:
            end_date = datetime.datetime.strptime(date, "%d-%m-%Y")
        except (TypeError, ValueError) as e:
            reports_logger.error(f"Ошибка {e} чтения даты из аргументов функции, требуется dd-mm-YYYY")
            return pd.DataFrame()
    start_date = end_date - relativedelta(months=3)
    reports_logger.debug(
        f'Выбран диапазон дат с {start_date.strftime("%d-%m-%Y")}  по {end_date.strftime("%d-%m-%Y")}'
    )

    filtered_by_date_df = filter_transactions_by_date(df=transactions, start_date=start_date, end_date=end_date)
    reports_logger.debug(f"Транзакции отфильтрованы по дате, выбрано {len(filtered_by_date_df)} записей")

    # Чистим данные, чтобы остались только расходы
    cleaned_for_calc_df = filtered_by_date_df[
        (filtered_by_date_df["Статус"] == "OK")
        & (filtered_by_date_df["Сумма операции"] < 0)
        & (filtered_by_date_df["Валюта платежа"] == "RUB")
    ]

    if cleaned_for_calc_df.empty:
        reports_logger.warning("Не найдено подходящих транзакций")
        return pd.DataFrame()

    reports_logger.debug(
        f"Транзакции отфильтрованы по типу, статусу и валюте, выбрано {len(cleaned_for_calc_df)} записей"
    )

    cleaned_for_calc_df["День недели"] = cleaned_for_calc_df["Дата операции"].map(lambda x: WEEKDAYS[x.weekday()])
    grouped_by_weekday_df = (
        cleaned_for_calc_df.groupby(by="День недели", as_index=False, group_keys=False)
        .agg({"Сумма операции": "sum"})
        .sort_values("Сумма операции")
    )
    reports_logger.debug("Функция spending_by_weekday выполнена успешно")
    return grouped_by_weekday_df
