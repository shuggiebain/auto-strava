import logging
import sys
import os
import requests
import time
import datetime
import configparser
import json
import pandas as pd
from pandas.io.json import json_normalize
from selenium import webdriver
from urllib.parse import urlparse

def log_init(save_log=False, log_path=None):

    timestamp = str(datetime.datetime.now().strftime("%Y%m%d_%H"))
    formatter = logging.Formatter('%(asctime)s %(name)-4s %(levelname)-4s %(lineno)04d %(message)s')

    streamHandler = logging.StreamHandler(sys.stdout)
    streamHandler.setFormatter(formatter)

    logging.getLogger("CONFIG").handlers = []
    logging.getLogger("CONFIG").setLevel('INFO')
    logging.getLogger("CONFIG").addHandler(streamHandler)
    logging.getLogger("CONFIG").propagate = False

    logging.getLogger("API AUTHENTICATION").handlers = []
    logging.getLogger("API AUTHENTICATION").setLevel('INFO')
    logging.getLogger("API AUTHENTICATION").addHandler(streamHandler)
    logging.getLogger("API AUTHENTICATION").propagate = False

    logging.getLogger("GET ACTIVITIES").handlers = []
    logging.getLogger("GET ACTIVITIES").setLevel('INFO')
    logging.getLogger("GET ACTIVITIES").addHandler(streamHandler)
    logging.getLogger("GET ACTIVITIES").propagate = False

    if save_log:

        if log_path is None:
            log_path = '.\logs'

        if not os.path.exists(log_path):
            os.makedirs(log_path)

    fileHandler = logging.FileHandler("{0}/{1}.log".format(log_path, 'Strava' + timestamp))
    fileHandler.setFormatter(formatter)
    logging.getLogger("CONFIG").addHandler(fileHandler)
    logging.getLogger("API AUTHENTICATION").addHandler(fileHandler)
    logging.getLogger("GET ACTIVITIES").addHandler(fileHandler)


def driver_configurations(driver_path):

    chromeoptions = webdriver.ChromeOptions()
    chromeoptions.add_argument('--no-sandbox')
    chromeoptions.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(chrome_options=chromeoptions, desired_capabilities=chromeoptions.to_capabilities(),
                              executable_path=driver_path)
    return driver


def generate_auth_code(driver_path, auth_url, email, pw):

    try:
        driver = driver_configurations(driver_path)
        driver.get(auth_url)
        logging.getLogger("API AUTHENTICATION").info("API Authorization in progress, generating authorization code")
        time.sleep(3)
        driver.find_element_by_xpath('//*[@id="login_form"]/div[1]/a').click()
        time.sleep(3)
        driver.find_element_by_id('email').send_keys(email)
        driver.find_element_by_id('pass').send_keys(pw)
        driver.find_element_by_id('loginbutton').click()
        time.sleep(3)
        driver.find_element_by_id('authorize').click()
        time.sleep(3)
        current_url = driver.current_url
        auth_code = urlparse(current_url).query.split('&')[1].split('=')[1]
        logging.getLogger("API AUTHENTICATION").info('Authentication code: ' + auth_code + 'successfully generated for:'
                                                     + email)
        return auth_code

    except Exception as e:
        logging.getLogger("API AUTHENTICATION").exception('Error authenticating request, please '
                                                          'verify credentials for' + email + ' ' + str(e))


def generate_access_token(auth_code, client_id, client_secret):

    if not os.path.exists('./permissions'):
        os.makedirs('./permissions')

    try:
        response = requests.post(
            url='https://www.strava.com/oauth/token',
            data={'client_id': client_id, 'client_secret': client_secret,
                  'code': auth_code, 'grant_type': 'authorization_code'})

        auth_token = response.json()
        logging.getLogger("API AUTHENTICATION").info('Access token generated using ' + auth_code)

        with open('./permissions/auth_token.json', 'w') as auth_file:
            json.dump(auth_token, auth_file)

        with open('./permissions/auth_token.json') as auth_file:
            strava_tokens = json.load(auth_file)
            access_token = strava_tokens['access_token']

        logging.getLogger("API AUTHENTICATION").info("Access token for " + str(client_id) + ": "
                                                     + str(access_token))
        return access_token

    except Exception as e:
        logging.getLogger("API AUTHENTICATION").exception('Error retrieving access token using ' + str(auth_code)
                                                          + str(e))


def scrape_activities(access_token, limit):

    page = 1
    activities_url = "https://www.strava.com/api/v3/activities"

    try:
        while True:
            request = requests.get(activities_url + '?access_token='
                                   + access_token + '&per_page=' + str(limit) + '&page=' + str(page))

            response = request.json()
            if len(response) == 0:
                logging.getLogger("GET ACTIVITIES").info('Scraping complete, no more activities found')
                break

            else:
                logging.getLogger("GET ACTIVITIES").info(str(len(response)) + ' activities found searching for more...')
                data = json_normalize(response)

                if not os.path.exists('./data'):
                    os.makedirs('./data')

                data.to_csv('./data/activities_page_' + str(page) + '_limit_' + str(limit)+'.csv')

                page += 1

    except Exception as e:
        logging.getLogger("GET ACTIVITIES").exception('Error scraping activities' + str(e))


def concatenate_data(folder_path):

    columns = ['average_heartrate', 'average_speed', 'distance', 'elapsed_time', 'gear_id',
               'max_heartrate', 'moving_time', 'start_date', 'start_latitude', 'start_longitude',
               'type', 'utc_offset', 'workout_type', 'start_date_local', 'name', 'start_latlng', 'end_latlng']

    file_paths = []

    try:

        for folder, subs, files in os.walk(folder_path):
            for filename in files:
                file_paths.append(os.path.abspath(os.path.join(folder, filename)))

        logging.getLogger("GET ACTIVITIES").info('Concatenating activity data')
        combined_csv = pd.concat([pd.read_csv(f, sep=',', usecols=columns) for f in file_paths])

        combined_csv.to_csv('.\combined_data.csv')

        data = pd.read_csv('.\combined_data.csv', sep=',', header='infer')
        return data

    except Exception as e:
        logging.getLogger("GET ACTIVITIES").exception("Error concatenating activities data " + str(e))


def config_init():
    try:
        config = configparser.RawConfigParser()
        config_file = '.\config2.ini'

        if os.path.isfile(config_file) == True:
            logging.getLogger("CONFIG").info('Configuration file found')

        try:
            file = open(config_file, 'r')
            file.close()
            config.read(config_file)

        except IOError as e:
            logging.getLogger("CONFIG").info('There was an error reading the file')
            raise e

        return config

    except Exception as e:
        logging.getLogger("CONFIG").exception('Error')


#
# Main
#

#Initializations
log_init(save_log=True, log_path=None)
config = config_init()

#Arguments
email = config.get('CREDENTIALS', 'email')
password = config.get('CREDENTIALS', 'pw')
id = config.get('CREDENTIALS', 'client_id')
secret = config.get('CREDENTIALS', 'client_secret')
driver_path = config.get('AUTHORIZATION', 'chrome_driver_path')
auth_url = config.get('AUTHORIZATION', 'authorization_url')
limit = config.get('ACTIVITIES', 'page_limit')

#Body
auth_code = generate_auth_code(driver_path=driver_path, auth_url=auth_url, email=email, pw=password)
access_token = generate_access_token(auth_code=auth_code, client_id=id, client_secret=secret)
scrape_activities(access_token=access_token, limit=limit)
df = concatenate_data(folder_path=os.path.join(sys.path[0], 'data'))