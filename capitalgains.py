import pandas as pd


def calc_gains(history: pd.DataFrame, splits: pd.DataFrame, start, end):
    history = history[["TradeTime", "B/S", "Amount", "Price in INR"]]
    # removing stock split entries
    history = history[history['Price in INR'].apply(lambda x: int(x) != 0)]
    history['Ratio'] = 0
    print(splits)
    for i in range(len(splits)):
        split = splits.iloc[i]
        condition = history['TradeTime'] <= split['Date']
        history.loc[condition, 'Ratio'] += split['Ratio']
    history.loc[history['Ratio'] == 0, 'Ratio'] = 1
    history.loc[:, 'SplitAdjusted'] = history['Amount'].astype(
        float) * history['Ratio']
    history.loc[:, 'SplitAdjustedPrice'] = history['Price in INR'] / \
        history['Ratio']
    print(history)

    buy_txn = history.loc[history['B/S'] == 'Bought', :]

    # FIFO before start
    prev_sales = history.loc[(history['B/S'] == 'Sold')
                             & (history['TradeTime'] < start), :]

    sell_fifo(buy_txn, prev_sales)

    print(buy_txn)

    new_sales = history.loc[(history['B/S'] == 'Sold')
                            & (history['TradeTime'] >= start), :]
    print(new_sales)

    data = sell_fifo(buy_txn, new_sales)

    print(buy_txn)

    print(data)


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
