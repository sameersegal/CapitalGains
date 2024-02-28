from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os

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

    return values
