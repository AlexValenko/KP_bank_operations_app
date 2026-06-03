import datetime
import json
import os

import requests
from dotenv import load_dotenv


def get_user_currencies(path_settings: str = "user_settings.json") -> list:
    """Функция принимает на вход файл пользовательских настроек (по умолчанию user_settings.json)
    и возвращает список валют для отображения их курса в рублях"""
    try:
        with open(path_settings) as file:
            user_settings = json.load(file)
    except FileNotFoundError:
        print("Settings file not found")
        return []
    return user_settings["user_currencies"]


def get_user_stocks(path_settings: str = "user_settings.json") -> list:
    """Функция принимает на вход файл пользовательских настроек (по умолчанию user_settings.json)
    и возвращает список акций для отображения их цены"""
    try:
        with open(path_settings) as file:
            user_settings = json.load(file)
    except FileNotFoundError:
        print("Settings file not found")
        return []
    return user_settings["user_stocks"]


def get_exchange_rate_api(base_currency: str = "RUB") -> None:
    """Функция принимает валюту, по умолчанию - рубль, формирует api запрос,
    сохраняет ответ в файл data/rates"""
    load_dotenv()
    apikey = os.getenv("API_KEY_RATES")
    url = f"https://v6.exchangerate-api.com/v6/{apikey}/latest/{base_currency}"

    try:
        response = requests.get(url=url, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Network error {e}")
        return None
    status_code = response.status_code
    if status_code == 200:
        try:
            result = response.json()
        except json.JSONDecodeError:
            print("Некорректный ответ сервера")
            return None
        # Записываем файл в КЭШ
        os.makedirs("data", exist_ok=True)
        with open("data/rates.json", "w") as f:
            json.dump(result, f, indent=4)
        return None
    else:
        print(f"Ошибка: статус-код {status_code}")
        print(response.text)
        return None


def check_rate_cache(cache_path="data/rates.json") -> bool:
    """Функция принимает список выбранных валют, проверяет наличие кэша,
    и сравнивает дату в файле с сегодняшним числом, если файл есть, и дата совпадает,
    то возвращает True, если файла нет или дата не сегодня, то False"""
    cache_file = cache_path
    if os.path.exists(cache_file):  # Проверяем что файл существует
        with open(cache_file, "r", encoding="utf-8") as f:
            exchange_rate_data = json.load(f)
        # Получаем дату последнего обновления файла
        date_updated_file = exchange_rate_data["time_last_update_utc"]
        date_updated_file_dt = datetime.datetime.strptime(date_updated_file, "%a, %d %b %Y %H:%M:%S %z")
        date_now_dt = datetime.datetime.now()
        if date_updated_file_dt.date() == date_now_dt.date():
            return True
        else:
            return False
    else:
        print("File not found")
        return False


def get_user_rates(cache_path="data/rates.json") -> list[dict]:
    """Проверяет есть ли актуальный кэш с курсом валют, да, то, берет данные из списка валют и вычисляет текущий курс,
    если нет, вызывает функцию получения данных по api, затем берет данные файла"""
    user_currencies = get_user_currencies()  # Список валют из файла user_settings
    if not user_currencies:
        return []

    is_check_valid = check_rate_cache()
    if is_check_valid is False:
        print("Файл не найден или не актуален, вызываю API")
        api_result = get_exchange_rate_api()
        if api_result is None:
            print("Не удалось получить данные через API")
            return []
    else:
        print("Используем актуальный кэш")
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            exchange_rate_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ошибка чтения файла кэша: {e}")
        return []

    # Проходим по списку выбранных валют и вычисляем актуальный курс
    currency_rates = []
    for item in user_currencies:
        try:
            value = round(1 / float(exchange_rate_data["conversion_rates"][item]), 2)
            rates = {"currency": item, "rate": value}
            currency_rates.append(rates)
        except (KeyError, ValueError, ZeroDivisionError) as e:
            print(f"Ошибка расчёта курса для {item}: {e}")
            continue
    return currency_rates


def get_current_stock_prices_api(tickers: list) -> list | None:
    """Принимает на вход список акций в виде тикеров, например 'SBER',
    получает текущие цены акций с Мосбиржи, и сохраняет в файл data/stocks_json
    возвращает список словарей с названием акций из списка и последней ценой"""
    url = "https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json"

    params = {
        "iss.meta": "off",  # отключаем метаданные
        "iss.only": "securities,marketdata",  # запрашиваем базовую информацию и рыночные данные
        "securities.columns": "SECID,SHORTNAME",  # базовая информация
        "marketdata.columns": "SECID,LAST,CHANGE,VALTODAY",  # рыночные данные: последняя цена, изменение, объём
    }
    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Network error {e}")
        return None
    status_code = response.status_code
    if status_code == 200:
        try:
            result = response.json()
        except json.JSONDecodeError:
            print("Некорректный ответ сервера")
            return None
        os.makedirs("data", exist_ok=True)
        with open("data/stocks.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

        all_stocks_price_list = result.get("marketdata").get("data")
        stocks_price_list = []
        for ticker in tickers:
            for _ in all_stocks_price_list:
                if _[0] == ticker:
                    out_dict = {"stock": ticker, "price": _[1]}
                    stocks_price_list.append(out_dict)
        return stocks_price_list

    else:
        print(f"Ошибка: статус-код {status_code}")
        print(response.text)
        return None
