import json

from src.utils import get_transaction_from_excel, get_cards_list_from_data, filter_transactions_by_date, filter_transactions_by_card, get_total_amount_and_cashback, get_top_transactions
from src.views import get_greeting, get_main_page_data
from src.external_api import get_user_currencies, get_exchange_rate_api, check_rate_cache, get_user_rates, get_user_stocks, get_current_stock_prices_api
import datetime

if __name__ == "__main__":
    # all_data_transactions = get_transaction_from_excel('data/operations.xlsx')
    # may_28 = datetime.datetime(year=2026, month=5, day=28)
    # transactions_since_28_may = filter_transactions_by_date(df=all_data_transactions, start_date=may_28)
    # print(transactions_since_28_may)
    # transactions_card_3753 = filter_transactions_by_card(df=transactions_since_28_may, card_number='*3753')
    # print(transactions_card_3753)
    # print(get_total_amount_and_cashback(df=transactions_card_3753, standard_cashback=True))
    # print(get_top_transactions_by_card(df=transactions_card_3753))

    # print(get_exchange_rate_api())
    # print(check_rate_cache(cache_path='exchange_rate_cached.json'))
    print(get_main_page_data(current_date='2026-04-08 12:00:00', path_excel_file='data/operations.xlsx'))





