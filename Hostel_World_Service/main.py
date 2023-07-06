"""
Project : Hostel World
Author : Ajeet
Date : July 03, 2023
"""
# import libraries
import os
import argparse
import json
import time
from typing import List, Dict, Optional
from config import log, Logging
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def scrape_hostel_world(url: str):
    options = ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--headless')
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_argument(f"--user-agent={Logging.user_agent}")
    driver = Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 10)

    log.info('................................Scraping the data from Hostel World................................')
    print('................................Scraping the data from Hostel World................................')
    log.info(f'The URL is : {url}')
    print(f'The URL is : {url}')

    driver.get(url)
    hostel_name = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1>div.title-2'))).text
    data = {"hostel_name": hostel_name}

    hostel_address = driver.find_element(By.CSS_SELECTOR, 'div.content>div.body-3').text
    data['hostel_address'] = hostel_address

    data['rooms_availability'] = {}

    room_category_container = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.availability-table')))
    for room_category in room_category_container:
        category_title = room_category.find_element(By.CSS_SELECTOR, 'div.title').text
        data['rooms_availability'][category_title] =[]
        rooms = room_category.find_elements(By.CSS_SELECTOR, 'div.room-container.desktop')
        for room in rooms:
            room_type = room.find_element(By.CSS_SELECTOR, 'div.room-title').text
            price = room.find_element(By.CSS_SELECTOR, 'div.price').text
            price_type = room.find_element(By.CSS_SELECTOR, 'div.rate-type').text
            capacity = room.find_element(By.CSS_SELECTOR, 'div.n-sleeps').text
            data['rooms_availability'][category_title].append({"room_type": room_type, "price": price, "price_type": price_type, "capacity": capacity})


    hostel_url = url
    data['hostel_url'] = hostel_url

    hostel_description = driver.find_element(By.CSS_SELECTOR, 'div.content.collapse-content').text.strip()
    data['hostel_description'] = hostel_description

    hostel_facilities = driver.find_elements(By.CSS_SELECTOR, 'ul.facility-sections>li')

    data['facilities'] = {}
    for facility in hostel_facilities:
        category = facility.find_element(By.TAG_NAME, 'h2').text
        facilities = [i.text.strip() for i in facility.find_elements(By.CSS_SELECTOR, 'ul.facilities>li')]
        data['facilities'][category] = facilities

    photo_container = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.property-photo-list')))
    driver.execute_script("arguments[0].scrollIntoView();",photo_container)
    time.sleep(1)
    hostel_images = [i.get_attribute('src') for i in
                     photo_container.find_elements(By.TAG_NAME, 'img')]
    data['hostel_images'] = hostel_images

    print("Data Scrapping Done!")
    log.info(f"scrapped data:\n{data}")
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape data from Hostel World')
    parser.add_argument('-u', '--url', help='Search URL', required=True)

    args = parser.parse_args()
    # https://www.hostelworld.com/pwa/hosteldetails.php/UNPLAN-Shinjuku/Tokyo/294428?from=2024-05-02&to=2024-05-03&guests=2&origin=microsite
    scrape_hostel_world(args.url)