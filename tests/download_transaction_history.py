from datetime import datetime
import pandas as pd
from main import download_current_prices
from sheets import fetch_data_from_spreadsheet
from dates import get_financial_year
from process import get_sales_for_year, get_entire_history_for_stock
from unittest import TestCase
import os
from dotenv import load_dotenv
load_dotenv()


class TestSheets(TestCase):

    def test_download_txn_history(self):

        SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
        RANGE_NAME = os.environ.get('SPREADSHEET_RANGE')

        data = fetch_data_from_spreadsheet(SPREADSHEET_ID, RANGE_NAME)
        self.assertTrue(data)
        self.assertTrue(len(data) > 680)

        # first row is a list of integers
        pd.DataFrame(data[1:], columns=data[0]).to_csv('txn_history.csv', index=False)

    def test_financial_year_dates(self):
        start, end = get_financial_year(datetime(2021, 4, 30))
        self.assertEqual(start, datetime(2021, 4, 1))
        self.assertEqual(end, datetime(2022, 3, 31))

        start, end = get_financial_year(datetime(2021, 3, 10))
        self.assertEqual(start, datetime(2020, 4, 1))
        self.assertEqual(end, datetime(2021, 3, 31))

    def test_sales_in_financial_year(self):
        start, end = get_financial_year()
        df = pd.read_csv('txn_history.csv')
        sales_this_year = get_sales_for_year(df, start, end)
        stocks_sold = sales_this_year['Symbol'].unique()
        stocks_sold.sort()
        print(stocks_sold)

    def test_appl_history(self):
        start, end = get_financial_year()
        df = pd.read_csv('txn_history.csv')
        code = "AAPL"
        history = get_entire_history_for_stock(df, code, end)
        print(history)

    def test_current_prices(self):
        df = download_current_prices()        
        self.assertTrue(len(df) > 0)
        self.assertTrue(df.columns.tolist() == ['Symbol', 'Share Price'])
        print(df.dtypes)