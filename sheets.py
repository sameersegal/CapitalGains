from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os

import pandas as pd

SERVICE_ACCOUNT_FILE = os.path.join(
    os.path.dirname(__file__), '.service-account.json')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def fetch_data_from_spreadsheet(spreadsheet_id, range_name):
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range=range_name).execute()
    values = result.get('values', [])

    service.close()

    return values

def download_ledger():
    SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
    RANGE_NAME = os.environ.get('SPREADSHEET_RANGE')

    data = fetch_data_from_spreadsheet(SPREADSHEET_ID, RANGE_NAME)    
    df = pd.DataFrame(data[1:], columns=data[0])

    # clean up    
    df = df[["Platform","Owner","Symbol","TradeTime","B/S","Amount","Price","Currency","Price in INR"]]
    df['TradeTime'] = pd.to_datetime(df['TradeTime'], format='mixed', dayfirst=False)
    df['Price in INR'] = df['Price in INR'].apply(
        lambda x: x.replace(",", "") if isinstance(x, str) else x)
    df['Price in INR'] = df['Price in INR'].astype(float)

    df['Price'] = df['Price'].apply(
        lambda x: x.replace(",", "") if isinstance(x, str) else x)
    df['Price'] = df['Price'].apply(
        lambda x: 0 if x == '' else x)    
    df['Price'] = df['Price'].astype(float)

    df['Amount'] = df['Amount'].apply(
        lambda x: x.replace(",", "") if isinstance(x, str) else x)
    df['Amount'] = df['Amount'].astype(float)    


    return df

def load_ledger():
    df = pd.read_csv('txn_history.csv')
    df['TradeTime'] = pd.to_datetime(df['TradeTime'], format='mixed', dayfirst=False)    
    return df

def download_current_prices():
    SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
    RANGES = os.environ.get('CURRENT_PRICE_RANGE')

    df = pd.DataFrame(columns=['Symbol','Quantity', 'Share Price', 'Currency'])
    for i, RANGE_NAME in enumerate(RANGES.split(',')):
        data = fetch_data_from_spreadsheet(SPREADSHEET_ID, RANGE_NAME)            
        data = pd.DataFrame(data[1:], columns=data[0])             
        data['Currency'] = 'USD' if i == 0 else 'INR'
        df = pd.concat([df, data[['Symbol','Quantity', 'Share Price', 'Currency']]])

    df['Share Price'] = df['Share Price'].apply(lambda x: float(x.replace(",", "")))

    return df
