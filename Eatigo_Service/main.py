"""
Project : Eatigo, Restaurants Asia
Author : Ajeet
Date : July 04, 2023
"""
# import libraries
import os
import argparse
import requests
import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from config import log, Logging
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def scrape_eatigo(url: str) -> Dict:

    options = ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--headless')
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_argument(f"--user-agent={Logging.user_agent}")
    driver = Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 10)

    driver.get(url)
    list_of_menu = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.restaurant-content--tabs-menu-table-row')))
    menu_items = [i.text for i in list_of_menu[1:]]
    driver.close()

    log.info('................................Scraping the data from Eatigo................................')
    log.info(f'The URL is : {url}')

    headers = {"User-Agent": Logging.user_agent}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    pattern = r'<script>\n\s{3}window\.__INITIAL_STATE__\s=\s(.+)'
    script_data = re.search(pattern=pattern, string=soup.prettify())[1].replace(';', '')

    json_data = json.loads(script_data)

    data = {
        "name": json_data['restaurantDetail']['restaurantData']['name'],
        "address": json_data['restaurantDetail']['restaurantData']['address'],
        "about": json_data['restaurantDetail']['restaurantData']['description'],
        # "url": json_data['restaurantDetail']['restaurantData']['websiteUrl'],
        "url": url,
        "picture_urls": [i['url'] for i in json_data['restaurantDetail']['restaurantData']['images']],
        "atmospheres": [i['name'] for i in json_data['restaurantDetail']['restaurantData']['atmospheres']],
        "spokenLanguages": [i['name'] for i in json_data['restaurantDetail']['restaurantData']['spokenLanguages']],
        "paymentOptions" : [i['name'] for i in json_data['restaurantDetail']['restaurantData']['paymentOptions']],
        "services": [i['name'] for i in json_data['restaurantDetail']['restaurantData']['services']],
        "operationHours": json_data['restaurantDetail']['restaurantData']['operationHours'],
        "menu_items": menu_items
        }

    log.info(f"data scrapping done.\n{data}")
    print("data scrapping done")
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape data from Eatigo')
    parser.add_argument('-u', '--url', help='Search URL', required=True)

    args = parser.parse_args()
    # https://eatigo.com/my/kuala-lumpur/en/r/contango-the-majestic-hotel-kuala-lumpur-5001183
    # https://eatigo.com/my/kuala-lumpur/en/r/latest-recipe-le-meridien-kl-1000534
    # https://eatigo.com/my/kuala-lumpur/en/r/hrc-sky-lounge-nu-sentral-shopping-centre-5007946
    print(scrape_eatigo(args.url))