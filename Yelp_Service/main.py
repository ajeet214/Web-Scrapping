"""
Project : Yelp, Shops
Author : Ajeet
Date : July 04, 2023
"""
# import libraries
import os
import argparse
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from config import log, Logging


def scrape_yelp(url: str) -> Dict:

    log.info('................................Scraping the data from Yelp................................')
    log.info(f'The URL is : {url}')

    headers = {"User-Agent": Logging.user_agent}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    name = soup.find('h1').text

    try:
        ref_website = soup.find("p", string="Business website")
        website = f"http://www.{ref_website.find_next_sibling('p').text}/"
    except AttributeError:
        website = None

    try:
        ref_mobile = soup.find('p', string="Phone number")
        mobile_number =  ref_mobile.find_next_sibling('p').text
    except AttributeError:
        mobile_number = None

    try:
        ref_address = soup.find('p', string="Get Directions")
        address =  ref_address.find_next_sibling('p').text
    except AttributeError:
        address = None

    about = soup.find('meta', property="og:description").get('content')

    url = soup.find('meta', property="og:url").get('content')

    try:
        amenities_list = soup.select('div[id^="expander-link-content-:"]')[1]
        amenities = [i.text for i in amenities_list.select('span[data-font-weight="semibold"]')]
    except IndexError:
        amenities = None

    container = soup.select_one('div[class^="photo-header-content__"]')

    try:
        ref_opening_hours = container.find('span', string="Open")
        opening_hours =  ref_opening_hours.find_next_sibling('span').text
    except AttributeError:
        opening_hours = None

    category = container.select_one('span[data-font-weight="semibold"]>a').text

    weekly_opening_hours_list = soup.find('tbody').select('tr')
    weekly_opening_hours = list(filter(None, [i.text for i in weekly_opening_hours_list]))

    data = {
        "name": name,
        "url": url,
        "place_category": category,
        "opening_hours": opening_hours,
        "weekly_opening_hours": weekly_opening_hours,
        "amenities": amenities,
        "place_about": about,
        "website": website,
        "mobile_number": mobile_number,
        "place_address": address
    }

    log.info(f"The scrapped data:\n{data}")

    return data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape data from Yelp')
    parser.add_argument('-u', '--url', help='Search URL', required=True)

    args = parser.parse_args()
    # https://www.yelp.com/biz/pavilion-kl-kuala-lumpur?osq=Shopping#location-and-hours
    # https://www.yelp.com/biz/sunway-velocity-mall-kuala-lumpur?page_src=related_bizes
    # https://www.yelp.com/biz/plaza-alam-sentral-shah-alam?page_src=related_bizes
    print(scrape_yelp(args.url))