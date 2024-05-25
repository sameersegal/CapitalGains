import pandas as pd

def get_sales_for_year(df, start, end, owner):
    # df['TradeTime'] = pd.to_datetime(df['TradeTime'], format='mixed', dayfirst=False)
    # print("original", df.shape, "\n")
    txns_current_year = df[(df['TradeTime'] >= start) & (df['TradeTime'] <= end)]
    # txns_current_year = txns_current_year[["Owner","Instrument","Symbol","TradeTime","B/S","Amount","Price","Currency","Price in INR"]]
    # print("filtering for financial year and cols", txns_current_year.shape, "\n")
    removed = txns_current_year[txns_current_year['Owner'].apply(lambda x: not x.startswith(owner))]
    # print("Removed the following transaction")
    # print(removed[['Owner','Symbol','B/S']], "\n")
    txns_current_year = txns_current_year[txns_current_year['Owner'].apply(lambda x: x.startswith(owner))]
    # print("filtering for DC ownership", txns_current_year.shape, "\n")
    sales_this_year = txns_current_year[txns_current_year['B/S'] == "Sold"]
    # print("filtering for sales", sales_this_year.shape, "\n")
    # print(sales_this_year.head())
    # print("Stocks sold this year")
    return sales_this_year

def get_entire_history_for_stock(df, code, end, owner):
    # df['TradeTime'] = pd.to_datetime(df['TradeTime'], format='mixed', dayfirst=False)
    # print("original", df.shape, "\n")
    history = df[(df['TradeTime'] <= end) & (df['Symbol'] == code) & (df['B/S'].apply(lambda x: x in ['Bought', 'Sold']))]
    # history = history[["Owner","Instrument","Symbol","TradeTime","B/S","Amount","Price","Currency","Price in INR"]]
    history = history[history['Owner'].apply(lambda x: x.startswith(owner))]
    return history

