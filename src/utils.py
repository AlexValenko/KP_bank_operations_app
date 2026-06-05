import datetime

import pandas as pd

""" При импорте файла выполняется валидация данных на соответствие столбцов таблицы.
 В функциях обработки повторная валидация не выполняется."""
REQUIRED_COLUMNS = [
    "Дата операции",
    "Дата платежа",
    "Номер карты",
    "Статус",
    "Сумма операции",
    "Валюта операции",
    "Кэшбэк",
    "Категория",
    "Описание",
    "Округление на инвесткопилку",
]


def get_transaction_from_excel(path_xlsx: str) -> pd.DataFrame | None:
    """Функция для считывания финансовых операций из файла Excel, принимает путь к файлу XLSX в качестве аргумента.
    Возвращает Dataframe библиотеки pandas для дальнейшей обработки данных.
    Функция проводит валидацию данных на наличие и соответствие названий столбцов"""

    try:
        # Парсит даты и преобразует числа с разделителем запятая, в числа
        transaction_df = pd.read_excel(path_xlsx, decimal=",", parse_dates=True)
    except FileNotFoundError:
        print("File not found")
        return None

    if transaction_df.empty:
        return None

    # Проверка наличия нужных столбцов
    imported_columns = set(transaction_df.columns)
    missing_columns = set(REQUIRED_COLUMNS).difference(imported_columns)
    if missing_columns:
        raise ValueError(f"Отсутствует один или несколько обязательных столбцов: {sorted(missing_columns)}")
    return transaction_df


def get_cards_list_from_data(df_trsnsactions: pd.DataFrame) -> list:
    """Получает список карт из DataFrame с операциями"""
    return df_trsnsactions["Номер карты"].unique().tolist()


def filter_transactions_by_date(
    df: pd.DataFrame, start_date: datetime = None, end_date: datetime = None
) -> pd.DataFrame:
    """Принимает на вход Dataframe с транзакциями, начальную и конечную дату в формате datetime,
    возвращает Dataframe с транзакциями, в пределах указанных дат.
    По умолчанию начальная дата 01.01.2000, конечная дата - сегодня"""
    if start_date is None:
        start_date = datetime.datetime(year=2000, month=1, day=1)
    if end_date is None:
        end_date = datetime.datetime.now()
    filtered_by_date_df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]
    return filtered_by_date_df


def filter_transactions_by_card(df: pd.DataFrame, card_number: str) -> pd.DataFrame:
    """Принимает на вход Dataframe с транзакциями и номер карты, возвращает Dataframe,
    в котором операции только с указанным номером карты. Номер карты в маскированном виде *0000"""
    filtered_by_card_transactions_df = df[df["Номер карты"] == card_number]
    return filtered_by_card_transactions_df


def get_total_amount_and_cashback(df: pd.DataFrame, standard_cashback: bool = True) -> dict:
    """Принимает Dataframe с транзакциями по одной карте, вычисляет общую сумму расходов и
    кешбэк (1 рубль на каждые 100 рублей). Если standard_cashback = False, берет сумму кэшбэк из таблицы"""

    # проверка, что в Dataframe только одна карта, иначе - пустой словарь
    unique_cards = df["Номер карты"].nunique(dropna=True)
    if unique_cards != 1:
        return {}
    card_number = df["Номер карты"].iloc[0]

    filtered_by_expenses = df[(df["Сумма операции"] < 0) & (df["Статус"] == "OK")]
    total_amount_by_card = abs(filtered_by_expenses["Сумма операции"].sum())

    if standard_cashback:
        total_cashback_by_card = round(total_amount_by_card / 100, 2)
    else:
        total_cashback_by_card = filtered_by_expenses["Кэшбэк"].sum()
    return {
        "last_digits": str(card_number),
        "total_spent": float(total_amount_by_card),
        "cashback": float(total_cashback_by_card),
    }


def get_top_transactions(df: pd.DataFrame) -> list:
    """Принимает Dataframe с транзакциями, сортирует транзакции по расходам,
    выводит топ-5 операций в виде словаря, или, если операций меньше - выводит все имеющиеся"""
    sorted_by_amount_transactions_df = df.sort_values(by=["Сумма операции"], ascending=True, na_position="first")
    filtered_empty_date_df = sorted_by_amount_transactions_df[sorted_by_amount_transactions_df["Дата платежа"].notna()]

    rows_count = len(filtered_empty_date_df)
    if rows_count > 5:
        rows_to_show = 5
    else:
        rows_to_show = rows_count

    top_transactions = filtered_empty_date_df.head(rows_to_show)
    top_transactions_list = []
    for index, item in top_transactions.iterrows():
        top_transactions_dict = {
            "date": (item["Дата платежа"]).strftime("%d-%m-%Y"),
            "amount": item["Сумма операции"],
            "category": item["Категория"],
            "description": item["Описание"],
        }
        top_transactions_list.append(top_transactions_dict)
    return top_transactions_list

def filter_transaction_by_category_for_cashback(df: pd.DataFrame, excluded_category: list, currency:str = "RUB") -> pd.DataFrame:
    """Функция фильтрует загруженный DataFrame: статус операции - ОК, Дата операции - есть, Сумма операции < 0 (списание)
    Категория не включает ['Пополнения', 'Переводы', 'Финансы', 'Проценты', 'Бонусы', 'Наличные']"""
    filtered_by_status_and_is_date = df[
        (df['Статус'] == "OK") &
        (df['Дата операции'].notna()) &
        (df['Сумма операции'] < 0) &
        (~df['Категория'].isin(excluded_category)) &
        (df['Валюта платежа'] == currency)]
    return filtered_by_status_and_is_date

