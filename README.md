# Capital Gains Calculation

Calculates Capital Gains for US stocks based on the Indian process. Fetches data from Google Spreadsheets and scrapes relevant data from other places.

## Process

**Pre-Processing**
1. Fetch Transaction History from Spreadsheet and save.
2. Fetch CII data and save.
3. Find stocks sold in the current financial year
4. Get the stock split history for each such stock
5. For each such stock sold calculate capital gains

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
$ python3 main.py --date 2024-03-01 --debug --owner DC --skip GOOG GOOGL HDFC
```