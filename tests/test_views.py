from src.views import get_greeting
import datetime

def test_get_greeting_morning()-> None:
    test_time = datetime.datetime(2023, 1, 1, 6, 0, 0)  # 6:00
    result = get_greeting(test_time)
    assert result == 'Доброе утро'

def test_get_greeting_noon()-> None:
    test_time = datetime.datetime(2023, 1, 1, 12, 1, 5)  # 12:01
    result = get_greeting(test_time)
    assert result == 'Добрый день'

def test_get_greeting_evening()-> None:
    test_time = datetime.datetime(2023, 1, 1, 18, 1, 5)  # 18:01
    result = get_greeting(test_time)
    assert result == 'Добрый вечер'

def test_get_greeting_night()-> None:
    test_time = datetime.datetime(2023, 1, 1, 0, 0, 0)  # 0:00
    result = get_greeting(test_time)
    assert result == 'Доброй ночи'

