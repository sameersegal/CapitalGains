from unittest import TestCase
import pandas as pd
from process import get_entire_history_for_stock
from dates import get_financial_year
from capitalgains import calc_gains


class TestGains(TestCase):

    def test_basic_entry(self):
        df = pd.read_csv('txn_history.csv')
        start, end = get_financial_year()
        code = "AAPL"
        history = get_entire_history_for_stock(df, code, end)
        history['Price in INR'] = history['Price in INR'].apply(lambda x: x.replace(",",""))
        history['Price in INR'] = history['Price in INR'].astype(float)
        history['Amount'] = history['Amount'].astype(float)
        splits = pd.DataFrame([
            {"Date": "2014-06-09", "Ratio": 4},
            {"Date": "2020-08-28", "Ratio": 7}
        ])
        splits['Date'] = pd.to_datetime(splits['Date'], format='%Y-%m-%d')
        calc_gains(history, splits, start, end)
