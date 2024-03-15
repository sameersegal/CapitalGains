from unittest import TestCase
import pandas as pd
from process import get_entire_history_for_stock
from dates import get_financial_year
from capitalgains import calc_gains, compute_profit
import numpy as np

class TestGains(TestCase):

    def test_basic_entry(self):
        df = pd.read_csv('txn_history.csv')
        start, end = get_financial_year()
        code = "AAPL"
        history = get_entire_history_for_stock(df, code, end)
        history['Price in INR'] = history['Price in INR'].apply(
            lambda x: x.replace(",", ""))
        history['Price in INR'] = history['Price in INR'].astype(float)
        history['Amount'] = history['Amount'].astype(float)
        splits = pd.DataFrame([
            {"Date": "2014-06-09", "Ratio": 4},
            {"Date": "2020-08-28", "Ratio": 7}
        ])
        splits['Date'] = pd.to_datetime(splits['Date'], format='%Y-%m-%d')
        calc_gains(history, splits, start, end)

    def test_profits(self):
        
        df = pd.DataFrame([
            {"Date Sold": "2023-11-13", "Quantity": 99.0, "Sale Price": 15370.80,
                "Cost Price": 1060.510000, "Purchase Date": "2010-07-02"},
            {"Date Sold": "2023-11-13", "Quantity": 1.0, "Sale Price": 15370.80,
                "Cost Price": 1050.994545, "Purchase Date": "2010-07-15"},
            {"Date Sold": "2023-11-13", "Quantity": 36.0, "Sale Price": 15370.97,
                "Cost Price": 1050.994545, "Purchase Date": "2010-07-15"},
            {"Date Sold": "2023-12-05", "Quantity": 103.0, "Sale Price": 16109.59,
                "Cost Price": 1050.994545, "Purchase Date": "2010-07-15"}
        ])

        result = compute_profit(df)

        print(np.sum(result['Tax@20']))