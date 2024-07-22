from datetime import datetime
import pandas as pd

# TODO: convert into one line


def get_sales_for_year(df, start, end, owner):
    txns_current_year = df[(df['TradeTime'] >= start)
                           & (df['TradeTime'] <= end)]
    txns_current_year = txns_current_year[txns_current_year['Owner'].apply(
        lambda x: x.startswith(owner))]
    sales_this_year = txns_current_year[txns_current_year['B/S'] == "Sold"]
    return sales_this_year

# TODO: convert into one line


def get_entire_history_for_stock(df: pd.DataFrame, code, end, owner):

    # preserve original dataframe
    df2 = df.copy()

    if code == "GOOG":
        # append GOOGL transactions as history before April 03, 2014
        # rename code to GOOG
        append_history = df2[(df2['TradeTime'] < datetime(2014, 4, 3)) & (
            df2['Symbol'] == 'GOOGL') & (df2['B/S'].apply(lambda x: x in ['Bought', 'Sold']))]
        # print("Data from GOOGL")
        # print(append_history)
        append_history.loc[:, 'Symbol'] = 'GOOG'
        append_history.loc[:, 'Price'] = append_history['Price'] / 2
        append_history.loc[:,
                           'Price in INR'] = append_history['Price in INR'] / 2
        df2 = pd.concat([append_history, df2])
        df2.sort_values(by='TradeTime', inplace=True)

    history = df2[(df2['TradeTime'] <= end) & (df2['Symbol'] == code) & (
        df2['B/S'].apply(lambda x: x in ['Bought', 'Sold']))]
    history = history[history['Owner'].apply(lambda x: x.startswith(owner))]

    if code == "GOOGL":
        # half the price of all acquisition costs before April 03, 2014
        googl_filter = history['TradeTime'] < datetime(2014, 4, 3)
        history.loc[googl_filter, 'Price in INR'] = history.loc[googl_filter, 'Price in INR'] / 2
        history.loc[googl_filter, 'Price'] = history.loc[googl_filter, 'Price'] / 2
    return history
