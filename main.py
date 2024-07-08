import numpy as np
from termcolor import colored
import argparse
from datetime import datetime
import os
import re
from sheets import download_ledger, download_current_prices, load_ledger
import pandas as pd
from dates import get_financial_year
from process import get_sales_for_year, get_entire_history_for_stock
from scraper import download_usd_to_inr, get_splits
from capitalgains import calc_gains, compute_profit
from dotenv import load_dotenv
load_dotenv()

debug: callable = None

def calculate_capital_gains(df, stocks_sold, start, end, **kwargs) -> pd.DataFrame:
    
    result = []

    for code in stocks_sold:
        print("\n")
        print(code)
        history = get_entire_history_for_stock(
            df, code, end, owner=kwargs['owner'])
        
        split_code = code
        if split_code == 'BOM:500209':
            split_code = 'INFY'

        splits = get_splits(split_code)
        print(splits.to_csv(index=False))

        data = calc_gains(history, splits, start, end)
        data = compute_profit(data)

        print(f"Tax for {code}: {data['Tax@20WI'].sum()/1e5:.2f}L")

        result.append({'Code': code, 'Cash':data['Cash'].sum(), 'Gain':data['Gain'].sum(), 'Tax': data['Tax@20WI'].sum()})        

    return pd.DataFrame(result)

def main(**kwargs):

    pd.set_option('display.float_format', lambda x: '%.2f' % x)
    
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

    if kwargs.get('consider_stocks', None):
        stocks_sold = kwargs['consider_stocks']
        start, end = get_financial_year()
        debug(f"Start: {start}, End: {end}")
    else:
        df = load_ledger()
        start, end = get_financial_year(kwargs['today'], debug=kwargs['debug'])
        debug(f"Start: {start}, End: {end}")
        sales_this_year = get_sales_for_year(df, start, end, owner=kwargs['owner'])
        stocks_sold = sales_this_year['Symbol'].unique()
        stocks_sold.sort()

        if kwargs.get('skip_stocks', None):
            stocks_sold = [x for x in stocks_sold if x not in kwargs['skip_stocks']]
            debug(f"Skipped the following stocks {kwargs['skip_stocks']}")

    debug(f"Considering only {stocks_sold}")

    if kwargs.get('simulation', False):
        
        df = load_ledger()
        prices = pd.read_csv('current_prices.csv')

        final_result = pd.DataFrame(columns=['Code', 'Cash', 'Gain', 'Tax'])
        usd_inr = download_usd_to_inr()
        for code in stocks_sold:            
            current_price = prices[prices['Symbol'] == code]['Share Price'].values[0]
            total_quantity = prices[prices['Symbol'] == code]['Quantity'].values[0]
            if code == "BOM:500209":
                total_quantity = 2154
            currency = prices[prices['Symbol'] == code]['Currency'].values[0]

            if not kwargs.get('consider_percentages', None):
                raise Exception("Please provide the percentage to sell for simulation")

            for percentage in kwargs['consider_percentages']:
                quantity = np.ceil(total_quantity * float(percentage) / 100)
                row = {
                    'Owner': kwargs['owner'],
                    'Symbol': code,
                    'TradeTime': datetime.today(),
                    'B/S': 'Sold',
                    'Amount': quantity * -1,
                    'Price': current_price,
                    'Currency': currency,                
                    'Price in INR': current_price * usd_inr if currency == 'USD' else current_price
                }
                
                new_df = pd.concat([df, pd.DataFrame([row])])                
                
                result = calculate_capital_gains(new_df, [code], start, end, **kwargs)
                result['Quantity'] = quantity
                result['Percentage'] = percentage
                final_result = pd.concat([final_result, result]) if len(final_result) > 0 else result

        print("\n\nSimulation Results")
        print(final_result.to_markdown(index=False, floatfmt=".2f"))
    else:
        df = load_ledger()
        result = calculate_capital_gains(df, stocks_sold, start, end, **kwargs)

        print(result.to_markdown(index=False))
        print(f"Total cash: {result['Cash'].sum()/1e5:.2f}L")
        print(f"Total gains: {result['Gain'].sum()/1e5:.2f}L")
        print(f"Total tax: {result['Tax'].sum()/1e5:.2f}L")
        

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
        "--consider-stocks", help="Consider only the following stock", required=False, nargs='+')
    parser.add_argument("--consider-percentages", help="Consider only the following percentages to sell", required=False, nargs='+')
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
    kwargs['consider_stocks'] = args.consider_stocks
    kwargs['consider_percentages'] = args.consider_percentages

    if kwargs['debug']:
        print(colored("Current configuration:", 'yellow'))
        for k, v in kwargs.items():
            print(colored(f"{k}: {v} ({type(v)})", 'yellow'))
        print("\n")

    main(**kwargs)
