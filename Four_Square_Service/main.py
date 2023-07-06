"""
Project : Four Square, Shops
Author : Ajeet
Date : July 04, 2023
"""
# import libraries
import os
import argparse
import requests
import re
import json
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from config import log, Logging


def scrape_four_square(url: str) -> Dict:

    log.info('................................Scraping the data from Four Square................................')
    log.info(f'The URL is : {url}')

    headers = {"User-Agent": Logging.user_agent}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    # this is another way to extract the data from the script
    # pattern = r'<script type="text/javascript">\n\s+fourSq\.queue\.push\(function\(\)\s\{fourSq\.venue\d\.desktop\.VenueDetailPage\.init\((.+)\);\}\);\n\s+</script>'
    # script_data = re.search(pattern=pattern, string=soup.prettify())[1]
    #
    # fixed_json_string = re.sub(r'(,\s+)([a-zA-Z]+)(:\s)', r'\1"\2"\3', script_data)
    # fixed_json_string = re.sub(r": '([a-z]*)',", r': "\1",' , fixed_json_string)
    # fixed_json_string = fixed_json_string.replace('relatedVenuesResponse:', '"relatedVenuesResponse":').replace('tips:', '"tips":').replace('venue:', '"venue":').replace('venueFlagConfig:', '"venueFlagConfig":').replace('undefined', '"undefined"')
    #
    # json_data = json.loads(fixed_json_string)
    # print(json_data.keys())

    # --------------------------------------------------------------------------
    primary_info = soup.select_one('div.primaryInfo')

    name = primary_info.select_one('h1.venueName').text

    try:
        canonical_name = primary_info.select_one('span.venueCanonicalName').text
    except AttributeError:
        canonical_name = None
    try:
        category = primary_info.select_one('div.categories').text
    except AttributeError:
        category = None
    try:
        venue_city = primary_info.select_one('span.venueCity').text
    except AttributeError:
        venue_city = None

    # --------------------------------------------------------------------------
    venue_details = soup.select_one('div.venueDetails')
    try:
        address = venue_details.select_one('div.adr').text
    except AttributeError:
        address = None
    try:
        opening = venue_details.select_one('span.open').text
    except AttributeError:
        opening = None
    try:
        mobile_number = venue_details.select_one('span.tel').text
    except AttributeError:
        mobile_number = None
    try:
        website = venue_details.select_one('a.url').get('href')
    except AttributeError:
        website = None
    try:
        facebook = venue_details.select_one('a.facebookPageLink').get('href')
    except AttributeError:
        facebook = None
    try:
        twitter = venue_details.select_one('a.twitterPageLink').get('href')
    except AttributeError:
        twitter = None
    try:
        instagram = venue_details.select_one('a.instagramPageLink').get('href')
    except AttributeError:
        instagram = None
    try:
        about = venue_details.select_one('div.descriptionBlock.sideVenueBlockRow').text
    except AttributeError:
        about = None
    #-------------------------------------------------------------------------------------
    url = soup.find('meta', property="og:url").get('content')

    data = {
        "name": name,
        "url": url,
        "canonical_name": canonical_name,
        "category": category,
        "venue_city": venue_city,
        "about": about,
        "address": address,
        "opening": opening,
        "mobile_number": mobile_number,
        "website": website,
        "instagram": instagram,
        "facebook": facebook,
        "twitter": twitter
    }

    log.info(f"The scrapped data:\n{data}")
    print(f"The scrapped data:\n{data}")

    return data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape data from Four Square')
    parser.add_argument('-u', '--url', help='Search URL', required=True)

    args = parser.parse_args()
    # https://foursquare.com/v/centralworld-%E0%B9%80%E0%B8%8B%E0%B8%99%E0%B8%97%E0%B8%A3%E0%B8%A5%E0%B9%80%E0%B8%A7%E0%B8%A5%E0%B8%94/4b0587fcf964a52002ab22e3
    # https://foursquare.com/v/sf-world-cinema-%E0%B9%80%E0%B8%AD%E0%B8%AA-%E0%B9%80%E0%B8%AD%E0%B8%9F-%E0%B9%80%E0%B8%A7%E0%B8%A5%E0%B8%94-%E0%B8%8B%E0%B9%80%E0%B8%99%E0%B8%A1%E0%B8%B2/4b46eb7df964a5209e2926e3?tasteId=52db1e24498ee80fc6445b9e
    # https://foursquare.com/v/centara-grand-at-centralworld/4b4a431cf964a5204a8126e3
    print(scrape_four_square(args.url))