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
    for i in range(len(prev_sales)):
        sold = prev_sales.iloc[i]['Amount'] * -1
        for j in range(len(buy_txn)):
            txn = buy_txn.iloc[j]
            if txn['Amount'] == 0:
                continue
            reduce_by = max(txn['Amount'], sold)
            sold -= reduce_by
            buy_txn.loc[j:1, 'Amount'] -= reduce_by
            if sold == 0:
                break

    print(buy_txn)
