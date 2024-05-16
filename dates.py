from datetime import datetime

from termcolor import colored

def get_financial_year(today=datetime.today(), debug=False):
    if today.month < 4:
        # Before April, the financial year starts last year
        start_year = today.year - 1
    else:
        # From April, the financial year starts this year
        start_year = today.year

    end_year = start_year + 1

    if debug:
        print(colored(f"Financial year: {start_year}-{end_year}",'yellow'))

    return datetime(start_year, 4, 1), datetime(end_year, 3, 31)
