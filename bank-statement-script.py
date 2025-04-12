from requests import Session
from dotenv import load_dotenv
from os import getenv
from datetime import datetime
from dateutil.relativedelta import relativedelta
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import logging
import csv
import io

bank_api_url = 'https://api.starlingbank.com'

class StarlingBankAPI:
    def __init__(self, token, cert_path):
        self._s = Session()
        
        self._s.headers.update({
            'Authorization': f'Bearer {token}'
        })
        
        # self._s.verify = cert_path
        
        # make request to get accountUid
        response = self._s.get(bank_api_url + '/api/v2/accounts')
        data = response.json()
        self.accountUid = data['accounts'][0]['accountUid']


    def get_bank_statement(self):
        # Get the current date as a datetime object
        current_date = datetime.now()

        # Subtract one month from the current date
        one_month_ago = current_date - relativedelta(months=1)

        # Format the dates as strings if needed
        current_date_str = current_date.strftime('%Y-%m-%d')
        one_month_ago_str = one_month_ago.strftime('%Y-%m-%d')

        logging.debug("One month ago:", one_month_ago_str)

        # GET bank statement for past month from starling bank using their api
        url = bank_api_url + f'/api/v2/accounts/{self.accountUid}/statement/downloadForDateRange'
        params = {
            'start': one_month_ago_str,
            'end': current_date_str
        }

        # set accept header to get pdf file
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
    def __init__(self, credentials_path, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id
        self.credentials = Credentials.from_service_account_file(credentials_path, scopes=['https://www.googleapis.com/auth/spreadsheets'])
        self.service = build('sheets', 'v4', credentials=self.credentials)
          
    def write_to_sheet(self, csv_content):

        sheet_name = 'Statement ' + datetime.now().strftime('%Y-%m-%d')

        # Parse the CSV content into rows
        csv_reader = csv.reader(io.StringIO(csv_content))
        rows = list(csv_reader)

        # Prepare the request body
        body = {
            'values': rows
        }

        # Write data to the specified sheet
        # sheet_range = f"{sheet_name}!A1"
        sheet_range = "Sheet1!A1"  # Change this to your desired range
        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=sheet_range,
            valueInputOption='RAW',
            body=body
        ).execute()


def send_email(email_address):
    print("This will send an email with the csv file attached hopefully!")

def main():
    # get bank statement
    csv_content = bank_api.get_bank_statement()
    
    # write to google sheet
    google_api.write_to_sheet(csv_content)
    
    # send email with the csv file attached
    send_email(email_address)

if __name__ == "__main__":
    # set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s:%(asctime)s - %(message)s'
    )
    
    # load environment variables
    load_dotenv()
    token = getenv('CLIENT_TOKEN')
    cert_path = getenv('CERT_PATH')
    
    email_address = getenv('EMAIL_ADDRESS')
    
    google_application_credentials = getenv('GOOGLE_APPLICATION_CREDENTIALS')
    spreadsheet_id = getenv('GOOGLE_SPREADSHEET_ID')
    
    bank_api = StarlingBankAPI(token, cert_path)
    
    google_api = GoogleSheetsAPI(google_application_credentials, spreadsheet_id)
    
    main()
    