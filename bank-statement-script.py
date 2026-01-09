# https://developers.google.com/resources/api-libraries/documentation/sheets/v4/python/latest/sheets_v4.spreadsheets.values.html#batchUpdate

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.errors import HttpError
from requests import Session
from dotenv import load_dotenv
from os import getenv
from datetime import datetime, timedelta
import logging
import csv
import io

bank_api_url = 'https://api.starlingbank.com'

class StarlingBankAPI:
    def __init__(self, token):
        self._s = Session()
        
        self._s.headers.update({
            'Authorization': f'Bearer {token}'
        })
        
        # self._s.verify = cert_path
        
        # make request to get accountUid
        response = self._s.get(bank_api_url + '/api/v2/accounts')
        data = response.json()
        self.accountUid = data['accounts'][0]['accountUid']


    def get_bank_statement(self, start_date=None):
        # Get the current date as a datetime object
        current_date = datetime.now()

        # Format the dates as strings 
        current_date_str = current_date.strftime('%Y-%m-%d')
        
        if start_date:
            start_date_str = start_date.strftime('%Y-%m-%d')
        else:
            # Subtract one week from the current date
            one_week_ago = current_date - timedelta(days=7)
            start_date_str = one_week_ago.strftime('%Y-%m-%d')

        # GET bank statement for past month from starling bank using their api
        url = bank_api_url + f'/api/v2/accounts/{self.accountUid}/statement/downloadForDateRange'
        params = {
            'start': start_date_str,
            'end': current_date_str
        }

        # set accept header to get csv file
        bank_api._s.headers.update({'Accept': 'text/csv'})

        response = self._s.get(url, params=params)

        if response.status_code == 200:
            # Extract the CSV content as text
            csv_content = response.text
            return csv_content
        else:
            logging.error(f"Failed to fetch the statement. Status code: {response.status_code}")
            logging.error(f"Response: {response.text}")


class GoogleSheetsAPI:
    def __init__(self):
        self._s = Session()
        
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        self.service = build('sheets', 'v4', credentials=creds)
        
        self.spreadsheet_id = getenv('SPREADSHEET_ID')
        self.spreadsheet_sheet = 'Statement'
        self.spreadsheet_range = 0
        
    def get_last_row(self):
        try:
            get_response = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=self.spreadsheet_sheet
            ).execute()

            values = get_response.get('values', [])

            if not values:
                print('No data found.')
                first_empty_row = 1
            else:
                # Find first row where the first column is empty
                first_empty_row = None
                for i, row in enumerate(values, start=1):  # start=1 because rows are 1-indexed
                    # Check if row is empty or first column is empty
                    if not row or not row[0] or row[0].strip() == '':
                        first_empty_row = i
                        break
                
                # If no empty row found, append after the last row
                if first_empty_row is None:
                    first_empty_row = len(values) + 1

            self.spreadsheet_range = self.spreadsheet_sheet + f'!A{first_empty_row}'
            return values[first_empty_row - 2]
        except HttpError as err:
            print(f"Google Sheets API error: {err}")

        except Exception as err:
            print(f"Unexpected error: {err}")
            

    def update_bank_sheet(self, statement_rows):
        try:            
            body = {
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {
                        "range": self.spreadsheet_range,
                        "majorDimension": "ROWS",
                        "values": statement_rows
                    }
                ]
            }
            
            update_response = self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body 
            ).execute()

        except HttpError as err:
            print(f"Google Sheets API error: {err}")

        except Exception as err:
            print(f"Unexpected error: {err}")


def main():
    # get last date that the spreadsheet was updated
    last_row = sheets_api.get_last_row()
    # Convert column 0 to date
    last_row_date = datetime.strptime(last_row[0], '%d/%m/%Y')
    
    # get bank statement
    bank_statement = bank_api.get_bank_statement(start_date=last_row_date)
    
    # edit the bank statement to take out of the titles
    statement_csv = io.StringIO(bank_statement)
    reader = csv.reader(statement_csv)
    next(reader) # skip the titles
    statement_rows = []

    for row in reader:
        # Convert columns 4 and 5 to float
        row[4] = float(row[4])
        row[5] = float(row[5])

        statement_rows.append(row)
        
    # trim the bank statement so it's from the last row in the sheet onwards
    last_row = last_row[:8]
    last_row[4] = float(last_row[4])
    last_row[5] = float(last_row[5])
    
    # Find where last_row appears in statement_rows and keep everything after it
    new_rows = []
    found_last_row = False

    for row in statement_rows:
        
        if found_last_row:
            # We've already found the last row, so keep this one
            new_rows.append(row)
        elif row == last_row:
            # This is the last row from the sheet, start keeping rows after this
            found_last_row = True

    statement_rows = new_rows
    # add to my google sheets spreadsheet
    sheets_api.update_bank_sheet(statement_rows)
    

if __name__ == "__main__":
    # set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s:%(asctime)s - %(message)s'
    )
    
    # load environment variables
    load_dotenv()
    token = getenv('STARLING_CLIENT_TOKEN')
    # cert_path = getenv('CERT_PATH')
    
    bank_api = StarlingBankAPI(token)
    sheets_api = GoogleSheetsAPI()
    
    main()
    