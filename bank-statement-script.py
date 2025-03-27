from requests import Session
from dotenv import load_dotenv
from os import getenv
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

bank_api_url = 'https://api.starlingbank.com'
google_sheets_api_url = 'https://sheets.googleapis.com'
spreadsheet_id = ...

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

def main():
    # Get the current date as a datetime object
    current_date = datetime.now()

    # Subtract one month from the current date
    one_month_ago = current_date - relativedelta(months=1)

    # Format the dates as strings if needed
    current_date_str = current_date.strftime('%Y-%m-%d')
    one_month_ago_str = one_month_ago.strftime('%Y-%m-%d')
    
    logging.debug("One month ago:", one_month_ago_str)
    
    # GET bank statement for past month from starling bank using their api
    url = bank_api_url + f'/api/v2/accounts/{bank_api.accountUid}/statement/downloadForDateRange'
    params = {
        'start': one_month_ago_str,
        'end': current_date_str
    }
    
    # set accept header to get pdf file
    bank_api._s.headers.update({'Accept': 'text/csv'})
    
    response = bank_api._s.get(url, params=params)
    
    if response.status_code == 200:
        # Extract the CSV content as text
        csv_content = response.text
        print(csv_content)  # Print the CSV content or process it further
    else:
        logging.error(f"Failed to fetch the statement. Status code: {response.status_code}")
        logging.error(f"Response: {response.text}")
    
    # GOOGLE SHEETS API - write the csv content to a google sheet
    # authenticate with google sheets api using oauth2
    
    # format it into a nice excel/csv file / maybe find out if this file could be persistent so that you add a sheet to it every time?
    url = google_sheets_api_url + f'/v4/spreadsheets/{spreadsheet_id}:batchUpdate'
    
    response = bank_api._s.post(url, json={
        'requests': [
            {
                'addSheet': {
                    'properties': {
                        'title': f"Statement {current_date_str}"
                    }
                }
            }
        ]
    })
    
    # e-mail to EMAIL_ADDRESS whenever the script is run

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
    
    bank_api = StarlingBankAPI(token, cert_path)
    
    main()
    