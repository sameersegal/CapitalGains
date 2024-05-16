from termcolor import colored
import argparse
from datetime import datetime
import os
import re
from sheets import fetch_data_from_spreadsheet
import pandas as pd
from dates import get_financial_year
from process import get_sales_for_year, get_entire_history_for_stock
from scraper import download_splits_data, extract_table
from capitalgains import calc_gains, compute_profit
from dotenv import load_dotenv
load_dotenv()


def download_ledger():
    SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
    RANGE_NAME = os.environ.get('SPREADSHEET_RANGE')

    data = fetch_data_from_spreadsheet(SPREADSHEET_ID, RANGE_NAME)
    return pd.DataFrame(data[1:], columns=data[0])


def main(**kwargs):

    if not os.path.exists('txn_history.csv'):
        df = download_ledger()
        df.to_csv('txn_history.csv', index=False)
    else:
        df = pd.read_csv('txn_history.csv')

    start, end = get_financial_year(kwargs['today'], debug=kwargs['debug'])
    sales_this_year = get_sales_for_year(df, start, end, owner=kwargs['owner'])
    stocks_sold = sales_this_year['Symbol'].unique()
    stocks_sold.sort()

    if kwargs.get('skip', None):
        print(stocks_sold)
        stocks_sold = [x for x in stocks_sold if x not in ['GOOG', 'GOOGL','HDFC']]
        print(stocks_sold)

    if kwargs.get('debug', False):
        print(f"Stocks sold this year after removing skipped ones {kwargs['skip']}")
        print(stocks_sold)

    # stocks_sold.tolist().remove("HDFC")
    # stocks_sold = ['AAPL','AMZN','BRK.B','DIS','GOOG','NFLX','OKTA','PYPL']
    # stocks_sold = ['GOOG','NFLX','OKTA','PYPL']
    # stocks_sold = ['NFLX','OKTA','PYPL']
    # stocks_sold = ['AAPL','AMZN','BRK.B','DIS','NFLX','OKTA','PYPL']

    result = []

    for code in stocks_sold:
        history = get_entire_history_for_stock(
            df, code, end, owner=kwargs['owner'])
        history['Price in INR'] = history['Price in INR'].apply(
            lambda x: x.replace(",", ""))
        history['Price in INR'] = history['Price in INR'].astype(float)
        history['Amount'] = history['Amount'].astype(float)

        # print(f"History for {code}")
        # print(history)

        html = download_splits_data(code)
        data = extract_table(code, html)
        # print(f"Splits for {code}")
        splits = pd.DataFrame(data, columns=["Date", "Splits"])
        r = re.compile(r'(\d+) for (\d+)')

        def extract_ratio(x):
            m = r.match(x)
            return int(m.group(1)) / int(m.group(2)) if m else 1

        splits.loc[:, 'Ratio'] = splits['Splits'].apply(
            lambda x: extract_ratio(x))
        # print(splits)

        data = calc_gains(history, splits, start, end)
        data = compute_profit(data)

        print(f"Tax for {code}: {data['Tax@20'].sum()/1e5:.2f}L")

        result.append({'Code': code, 'Tax': data['Tax@20'].sum()})

        # calc_gains(history, pd.DataFrame(), start, end)

    result = pd.DataFrame(result)
    print(result)
    print(f"Total tax: {result['Tax'].sum()/1e5:.2f}L")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--date", help="A date in the format YYYY-MM-DD", required=False)
    parser.add_argument(
        "--owner", help="Owner of the stock e.g. DC", required=True, nargs='+')
    parser.add_argument(
        "--skip", help="Skip the following stocks", required=False, nargs='+')
    parser.add_argument("--debug", help="Debug mode", action="store_true")

    kwargs = {}
    args = parser.parse_args()

    if args.date:
        kwargs['today'] = pd.to_datetime(args.date)
    else:
        kwargs['today'] = datetime.today()

    kwargs['debug'] = args.debug

    kwargs['owner'] = args.owner[0]

    if args.skip:
        kwargs['skip'] = args.skip

    if kwargs['debug']:
        print(colored("Current configuration:", 'yellow'))
        for k, v in kwargs.items():
            print(colored(f"{k}: {v} ({type(v)})", 'yellow'))

    main(**kwargs)
