import pandas as pd

# TODO: convert into one line
def get_sales_for_year(df, start, end, owner):
    txns_current_year = df[(df['TradeTime'] >= start) & (df['TradeTime'] <= end)]    
    txns_current_year = txns_current_year[txns_current_year['Owner'].apply(lambda x: x.startswith(owner))]
    sales_this_year = txns_current_year[txns_current_year['B/S'] == "Sold"]
    return sales_this_year

# TODO: convert into one line
def get_entire_history_for_stock(df, code, end, owner):
    history = df[(df['TradeTime'] <= end) & (df['Symbol'] == code) & (df['B/S'].apply(lambda x: x in ['Bought', 'Sold']))]    
    history = history[history['Owner'].apply(lambda x: x.startswith(owner))]
    return history

