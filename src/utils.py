import pandas as pd
import datetime

def get_transaction_from_excel(path_xlsx: str) -> pd.DataFrame|None:
    """Функция для считывания финансовых операций из файла Excel, принимает путь к файлу XLSX в качестве аргумента.
    Возвращает Dataframe библиотеки pandas для дальнейшей обработки данных"""
    try:
        # Парсит даты и преобразует числа с разделителем , в числа
        transaction_df = pd.read_excel(path_xlsx, decimal=',', parse_dates=True)
    except FileNotFoundError:
        print("File not found")
        return None
    return transaction_df

def get_cards_list_from_data(df_trsnsactions:pd.DataFrame) -> list:
    """Получает список карт из DataFrame с операциями"""
    return df_trsnsactions['Номер карты'].unique().tolist()

def filter_transactions_by_date(df: pd.DataFrame, start_date:datetime=None, end_date:datetime=None) -> pd.DataFrame:
    """Принимает на вход Dataframe с транзакциями, начальную и конечную дату в формате datetime,
    возвращает Dataframe с транзакциями, в пределах указанных дат.
    По умолчанию начальная дата 01.01.2000, конечная дата - сегодня"""
    if start_date is None:
        start_date = datetime.datetime(year=2000, month=1, day=1)
    if end_date is None:
        end_date = datetime.datetime.now()
    filtered_by_date_df = df[
        (df['Дата операции'] >= start_date) & (df['Дата операции'] <= end_date)]
    return filtered_by_date_df

