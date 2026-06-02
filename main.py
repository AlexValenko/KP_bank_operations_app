from src.utils import get_transaction_from_excel, get_cards_list_from_data, filter_transactions_by_date, filter_transactions_by_card, get_total_amount_and_cashback, get_top_transactions_by_card
from src.views import get_greeting
import datetime

if __name__ == "__main__":
    all_data_transactions = get_transaction_from_excel('data/operations.xlsx')
    may_28 = datetime.datetime(year=2026, month=5, day=28)
    transactions_since_28_may = filter_transactions_by_date(df=all_data_transactions, start_date=may_28)
    print(transactions_since_28_may)
    transactions_card_3753 = filter_transactions_by_card(df=transactions_since_28_may, card_number='*3753')
    print(transactions_card_3753)
    print(get_total_amount_and_cashback(df=transactions_card_3753, standard_cashback=True))
    print(get_top_transactions_by_card(df=transactions_card_3753))


