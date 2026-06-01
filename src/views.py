import datetime
from xmlrpc.client import DateTime


def get_greeting(current_time:DateTime|None=None) -> str:
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

print(get_greeting())
