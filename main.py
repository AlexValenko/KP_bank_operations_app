from src.utils import get_transaction_from_excel, get_cards_list_from_data, filter_transactions_by_date
from src.views import get_greeting
import datetime

if __name__ == "__main__":
    all_data_transactions = get_transaction_from_excel('data/operations.xlsx')
    # print(type(all_data_transactions))
    # print(all_data_transactions.head(2))
    # filtered_last_week_df = all_data_transactions[all_data_transactions['Дата операции'] >= datetime(2026, 5, 25)]
    # print(filtered_last_week_df)
    may_28 = datetime.datetime(year=2026, month=5, day=28)
    transactions_since_28_may = filter_transactions_by_date(df=all_data_transactions, start_date=may_28)
    print(transactions_since_28_may)
    # cards = get_cards_list_from_data(df_trsnsactions=all_data_transactions)
    # print(cards)
    # print(type(cards))
