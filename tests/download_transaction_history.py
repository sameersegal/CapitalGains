from datetime import datetime
import pandas as pd
from sheets import fetch_data_from_spreadsheet
from dates import get_financial_year
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
        # df['TradeTime'] = 07/07/1997
        df['TradeTime'] = pd.to_datetime(df['TradeTime'], format='mixed', dayfirst=False)
        txns_current_year = df[(df['TradeTime'] >= start) & (df['TradeTime'] <= end)]
        print(txns_current_year)