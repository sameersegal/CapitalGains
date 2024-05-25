import pandas as pd
from dates import get_financial_year

def print_df(df: pd.DataFrame):
    print(df.to_markdown(index=False))


def calc_gains(history: pd.DataFrame, splits: pd.DataFrame, start, end):
    history = history[["TradeTime", "B/S", "Amount", "Price", "Price in INR", "Owner"]]
    # removing stock split entries
    history = history[history['Price in INR'].apply(lambda x: int(x) != 0)]
    history['Ratio'] = 0
    
    for i in range(len(splits)):
        split = splits.iloc[i]
        condition = history['TradeTime'] <= split['Date']
        history.loc[condition, 'Ratio'] += split['Ratio']
    history.loc[history['Ratio'] == 0, 'Ratio'] = 1
    history.loc[:, 'SplitAdjusted'] = history['Amount'].astype(
        float) * history['Ratio']
    history.loc[:, 'SplitAdjustedPrice'] = history['Price in INR'] / \
        history['Ratio']
    print("\nHistory")
    print_df(history)

    buy_txn = history.loc[history['B/S'] == 'Bought', :]

    # FIFO before start
    prev_sales = history.loc[(history['B/S'] == 'Sold')
                             & (history['TradeTime'] < start), :]

    sell_fifo(buy_txn, prev_sales)

    print("\nAdjusting for previous sales")
    print_df(buy_txn)

    new_sales = history.loc[(history['B/S'] == 'Sold')
                            & (history['TradeTime'] >= start), :]
    # print(new_sales)

    data = sell_fifo(buy_txn, new_sales)

    # print(buy_txn)

    print("\nCalculating purchase price & quantity for sales in current FY")
    print_df(data)

    return data


def sell_fifo(buys, sales):
    df = []
    for i in range(len(sales)):
        sold = sales.iloc[i]['SplitAdjusted'] * -1
        sale_index = sales.index[i]
        for j in range(len(buys)):
            txn = buys.iloc[j]
            buy_index = buys.index[j]
            if txn['SplitAdjusted'] == 0:
                continue
            reduce_by = min(txn['SplitAdjusted'], sold)
            sold -= reduce_by
            df.append({
                'Date Sold': sales.at[sale_index, 'TradeTime'],
                'Quantity': reduce_by,
                'Sale Price': sales.at[sale_index, 'SplitAdjustedPrice'],
                'Cost Price': txn['SplitAdjustedPrice'],
                'Purchase Date': txn['TradeTime']
            })
            buys.at[buy_index, 'SplitAdjusted'] -= reduce_by
            if sold == 0:
                break

    return pd.DataFrame(df)


def compute_profit(df):

    # print(df)

    df.loc[:, 'Date Sold'] = pd.to_datetime(df['Date Sold'], format='%Y-%m-%d')
    df.loc[:, 'Purchase Date'] = pd.to_datetime(
        df['Purchase Date'], format='%Y-%m-%d')

    def get_fy(date):
        start, end = get_financial_year(date)
        return f"{start.year}-{end.year % 100}"

    df.loc[:, 'FY Selling'] = df.apply(
        lambda x: get_fy(x['Date Sold']), axis=1)
    df.loc[:, 'FY Purchase'] = df.apply(
        lambda x: get_fy(x['Purchase Date']), axis=1)
    
    # print(df)
    
    cii = pd.read_csv('cii.csv')

    df = df.merge(cii, left_on='FY Selling', right_on='Financial Year')

    # print(df)

    df = df.rename(columns={'CII': 'CII Selling'})
    df = df.drop(columns=['Financial Year'])

    df = df.merge(cii, left_on='FY Purchase', right_on='Financial Year')
    df = df.rename(columns={'CII': 'CII Purchase'})
    df = df.drop(columns=['Financial Year'])

    df.loc[:, 'Indexed Cost Price'] = df['Cost Price'] * \
        (df['CII Selling'] / df['CII Purchase'])
    
    # df.loc[:, 'Profit'] = (df['Sale Price'] - df['Indexed Cost Price']) * df['Quantity']

    # Long term capital gains with indexation benefits
    df.loc[:, 'Cash'] = df['Sale Price'] * df['Quantity']

    df.loc[:, 'Gain'] = (df['Sale Price'] - df['Indexed Cost Price']) * df['Quantity']

    df.loc[:, 'Tax@20WI'] = (df['Sale Price'] - df['Indexed Cost Price']) * df['Quantity'] * 0.2

    df.loc[:, 'Tax@20'] = (df['Sale Price'] - df['Cost Price']) * df['Quantity'] * 0.2


    print("\nFinal Calculation")
    print_df(df)

    return df
