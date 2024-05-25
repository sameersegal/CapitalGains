from termcolor import colored
import argparse
from datetime import datetime
import os
import re
from sheets import download_ledger, download_current_prices
import pandas as pd
from dates import get_financial_year
from process import get_sales_for_year, get_entire_history_for_stock
from scraper import get_splits
from capitalgains import calc_gains, compute_profit
from dotenv import load_dotenv
load_dotenv()

def calculate_capital_gains(df, stocks_sold, start, end, **kwargs):
    
    result = []

    for code in stocks_sold:
        print("\n")
        print(code)
        history = get_entire_history_for_stock(
            df, code, end, owner=kwargs['owner'])
        history['Price in INR'] = history['Price in INR'].apply(
            lambda x: x.replace(",", "") if isinstance(x, str) else x)
        history['Price in INR'] = history['Price in INR'].astype(float)
        history['Amount'] = history['Amount'].astype(float)

        # print(f"History for {code}")
        # print(history)

        splits = get_splits(code)
        print(splits.to_csv(index=False))

        data = calc_gains(history, splits, start, end)
        data = compute_profit(data)

        print(f"Tax for {code}: {data['Tax@20'].sum()/1e5:.2f}L")

        result.append({'Code': code, 'Gain':data['Gain'].sum(), 'Tax': data['Tax@20'].sum()})

        # calc_gains(history, pd.DataFrame(), start, end)

    result = pd.DataFrame(result)
    print(result)
    print(f"Total gains: {result['Gain'].sum()/1e5:.2f}L")
    print(f"Total tax: {result['Tax'].sum()/1e5:.2f}L")

def main(**kwargs):
    
    # download file dependencies
    def debug(*args):
        if kwargs['debug']:
            args = ' '.join([str(a) for a in args])
            print(colored(args,'yellow'))
    
    if not kwargs['skip_download']:
        if os.path.exists('txn_history.csv'):
            os.remove('txn_history.csv')
        if os.path.exists('current_prices.csv'):
            os.remove('current_prices.csv')
    else:
        debug("Not deleting old files because --skip-download is set")

    if not os.path.exists('txn_history.csv'):
        df = download_ledger()
        df.to_csv('txn_history.csv', index=False)
        debug("Downloaded Investment Ledger from Google Sheets")

    if kwargs.get('simulation',False) and not os.path.exists('current_prices.csv'):        
        df = download_current_prices()
        df.to_csv('current_prices.csv', index=False)
        debug("Downloaded Current Share Prices from Google Sheets")

    start = None
    end = None

    if kwargs.get('consider_stock', None):
        stocks_sold = kwargs['consider_stock']
        start, end = get_financial_year()
        debug(f"Start: {start}, End: {end}")
    else:
        df = pd.read_csv('txn_history.csv')
        start, end = get_financial_year(kwargs['today'], debug=kwargs['debug'])
        debug(f"Start: {start}, End: {end}")
        sales_this_year = get_sales_for_year(df, start, end, owner=kwargs['owner'])
        stocks_sold = sales_this_year['Symbol'].unique()
        stocks_sold.sort()

        if kwargs.get('skip_stocks', None):
            stocks_sold = [x for x in stocks_sold if x not in kwargs['skip_stocks']]
            debug(f"Skipped the following stocks {kwargs['skip_stocks']}")

    debug(f"Considering only {stocks_sold}")

    if kwargs.get('consider_amounts', None):
        pass

    df = pd.read_csv('txn_history.csv')
    calculate_capital_gains(df, stocks_sold, start, end, **kwargs)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--simulation', help='Run in simulation mode', 
    action='store_true')
    parser.add_argument('--skip-download', help='Skip download of files', action='store_true')
    parser.add_argument(
        "--date", help="A date in the format YYYY-MM-DD", required=False)
    parser.add_argument(
        "--owner", help="Owner of the stock e.g. DC", required=True, nargs='+')
    parser.add_argument(
        "--skip-stocks", help="Skip the following stocks", required=False, nargs='+')
    parser.add_argument(
        "--consider-stock", help="Consider only the following stock", required=False)
    parser.add_argument("--consider-amounts", help="Consider only the following amounts to sell", required=False, nargs='+')
    parser.add_argument("--debug", help="Debug mode", action="store_true")

    kwargs = {}
    args = parser.parse_args()

    kwargs['simulation'] = args.simulation
    kwargs['skip_download'] = args.skip_download

    if args.date:
        kwargs['today'] = pd.to_datetime(args.date)
    else:
        kwargs['today'] = datetime.today()

    kwargs['debug'] = args.debug

    kwargs['owner'] = args.owner[0]

    kwargs['skip_stocks'] = args.skip_stocks
    kwargs['consider_stock'] = args.consider_stock
    kwargs['consider_amounts'] = args.consider_amounts

    if kwargs['debug']:
        print(colored("Current configuration:", 'yellow'))
        for k, v in kwargs.items():
            print(colored(f"{k}: {v} ({type(v)})", 'yellow'))
        print("\n")

    main(**kwargs)
