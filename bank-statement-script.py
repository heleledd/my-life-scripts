from requests import Session
from dotenv import load_dotenv
from os import getenv
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

base_url = 'https://api.starlingbank.com'

class StarlingBankAPI:
    def __init__(self, token, cert_path):
        self._s = Session()
        
        self._s.headers.update({
            'Authorization': f'Bearer {token}'
        })
        
        self._s.verify = cert_path
        
        # make request to get accountUid
        response = self._s.get(base_url + '/api/v2/accounts')
        data = response.json()
        self.accountUid = data['accounts']['accountUid']

def main():
    # Subtract one month from the current date
    # date format should be YYYY-MM-DD
    current_date = datetime.now().strftime('%Y-%m-%d')
    one_month_ago = current_date - relativedelta(months=1)
    logging.debug("One month ago:", one_month_ago.strftime('%Y-%m-%d'))
    
    # GET bank statement for past month from starling bank using their api
    url = base_url + '/api/v2/accounts/{{accountUid}}/statement/downloadForDateRange'
    params = {
        'start': one_month_ago,
        'end': current_date
    }
    
    response = bank_api._s.get(url, params)
    
    print('i want to see the response...')
    # format it into a nice excel/csv file / maybe find out if this file could be persistent so that you add a sheet to it every time?
    
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
    