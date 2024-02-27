from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
load_dotenv()

# Path to your service account key file
SERVICE_ACCOUNT_FILE = os.path.join(
    os.path.dirname(__file__), '.service-account.json')

# The scopes required for the Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID of your Google Sheet (can be taken from its URL)
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
# Adjust the range according to your needs
RANGE_NAME = os.environ.get('SPREADSHEET_RANGE')

def main():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        for row in values[:5]:
            # Print columns A and B, which correspond to indices 0 and 1.
            # Adjust according to your data structure
            print(f'{row[0]}, {row[1]}')

if __name__ == '__main__':
    main()
