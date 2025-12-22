import requests
from datetime import datetime
from dotenv import load_dotenv
from os import getenv

national_rail_link = 'https://opendata.nationalrail.co.uk'

def authenticate(username, password):
    # ask
    data = {'username': username, 'password': password}
    response = requests.post(national_rail_link + '/authenticate', data)
    
    response_json = response.json()
    my_token = response_json.get('token')
    return my_token


def get_data(token):
    url = national_rail_link + '/api/staticfeeds/3.0/timetable'
    headers = {'X-Auth-Token': token}
    response = requests.get(url, headers=headers)
    

    # Get the current date
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"timetabling_{timestamp}.zip"
    
    with open(file_name, "wb") as f:
        f.write(response.content)


def main(username, password):
    token = authenticate(username, password)
    get_data(token)
    
    
if __name__ == "__main__":
    # get username and password from your .env file
    load_dotenv()
    username = getenv('USER_NATIONAL_RAIL')
    password = getenv('USER_NATIONAL_PASS')
    
    main(username, password)
