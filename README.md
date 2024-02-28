# Capital Gains Calculation

Calculates Capital Gains for US stocks based on the Indian process. Fetches data from Google Spreadsheets and scrapes relevant data from other places.

## Process

**Pre-Processing**
1. Fetch Transaction History from Spreadsheet and save.
2. Find stocks sold in the current financial year
3. Find stocks sold
4. For each such stock sold calculate capital gains
5. Get the stock split history for each such stock

**Capital Gains Calculation**
1. Inputs (for 1 stock): 
   1. Complete transaction history
   2. Split history
   3. Currency Conversion Rates
2. Adjust for Stock Splits
   1. Increase quantity
   2. Decrease price
3. Adjust for previous sales - FIFO
4. Compute new table:
   1. Quantity Sold
   2. Selling Price
   3. Cost Price
5. Convert into INR
6. Adjust with Indexation (CII ratios)

**Questions**
1. What happens in case of mergers and acquisitions?

## Developer Notes
```
$ poetry shell
$ poetry install
$ poetry run python3 main.py
```