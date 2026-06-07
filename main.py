import json

import pandas as pd

from src.utils import get_transaction_from_excel, get_cards_list_from_data, filter_transactions_by_date, filter_transactions_by_card, get_total_amount_and_cashback, get_top_transactions
from src.views import get_greeting, get_main_page_data
from src.external_api import get_user_currencies, get_exchange_rate_api, check_rate_cache, get_user_rates, get_user_stocks, get_current_stock_prices_api
from src.services import get_cashback_categories, investment_bank
from src.reports import spending_by_category, spending_by_weekday
import datetime

if __name__ == "__main__":
    all_data_transactions = get_transaction_from_excel('tests/test_data/test_operations.xlsx')
    # print(get_main_page_data(current_date='2026-03-20 12:00:02', path_excel_file='tests/test_data/test_operations.xlsx'))

    # test_df = get_cashback_categories(data=all_data_transactions, year=2026, month=3)
    # print(test_df)
    # print(investment_bank(month='2026-03', transactions=all_data_transactions, limit=50))
    # all_data_transactions = get_transaction_from_excel(path_xlsx='tests/test_data/test_operations.xlsx')
    # all_data_transactions = get_transaction_from_excel(path_xlsx='data/operations.xlsx')
    # month_invest_sum = investment_bank(month='2026-04', transactions=all_data_transactions, limit=50)
    # print(month_invest_sum)
    # kat = spending_by_weekday(transactions=all_data_transactions)
    # result_dict = spending_by_weekday(transactions=all_data_transactions, date='01-04-2026').to_dict()
    # print(result_dict)
    kat_dict = spending_by_weekday(transactions=all_data_transactions, date='01-04-2026').to_dict('records')
    print(kat_dict)
    kat = spending_by_category(transactions=all_data_transactions, category='Медицина', date='01-06-2026').to_dict('records')
    print(kat)










