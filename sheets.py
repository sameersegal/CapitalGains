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
    return pd.DataFrame(data[1:], columns=data[0])

def download_current_prices():
    SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
    RANGES = os.environ.get('CURRENT_PRICE_RANGE')

    df = pd.DataFrame(columns=['Symbol','Share Price'])
    for RANGE_NAME in RANGES.split(','):
        data = fetch_data_from_spreadsheet(SPREADSHEET_ID, RANGE_NAME)            
        data = pd.DataFrame(data[1:], columns=data[0])             
        df = pd.concat([df, data[['Symbol','Share Price']]])

    df['Share Price'] = df['Share Price'].apply(lambda x: float(x.replace(",", "")))

    return df
