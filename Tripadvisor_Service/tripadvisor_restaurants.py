"""
Project : Scrape Restaurant information from the Tripadvisor
Author : Ajeet
Date : June 30, 2023
"""
import re
import requests
import json
from typing import Dict
from bs4 import BeautifulSoup, element
from config import Logging
import argparse

def retrieve_original_image(img: str) -> str:
    return img.replace('photo-s', 'photo-o').replace('photo-f', 'photo-o').replace('photo-t', 'photo-o').replace('photo-l', 'photo-o')

def retrieve_restaurant_images(container: element.Tag) -> str:

    l_images = container.select('div.prw_rup.prw_common_basic_image.photo_widget.large.landscape')
    m_images = container.select_one('div.mini_photos_container').select('img')

    all_images = [retrieve_original_image(i.find('img').get('data-lazyurl')) for i in l_images[2:]]+[retrieve_original_image(i.get('data-lazyurl')) for i in m_images]

    return ', '.join(all_images)

def scrape_restaurant_info(url: str) -> Dict:

    response = requests.get(url, headers={"User-Agent": Logging.user_agent})
    soup = BeautifulSoup(response.text, 'html.parser')

    image_container = soup.select_one('div.mosaic_photos')
    restaurant_images = retrieve_restaurant_images(image_container)

    pattern = r'<script>\s+window.__WEB_CONTEXT__=(.+);\(this\.\$WP=this\.\$WP\|\|\[\]\)'
    script_data = re.search(pattern=pattern, string=soup.prettify())

    json_data = json.loads(script_data[1].replace("pageManifest", '"pageManifest"'))

    responses = json_data['pageManifest']['redux']['api']['responses']
    location = re.search(pattern=r'/data/[0-9.]+/location/\d+', string=str(responses)).group()

    overview = re.search(pattern=r'/data/[0-9.]+/restaurant/\d+/overview', string=str(responses)).group()


    restaurant_name = responses[location]['data']['name']
    try:
        restaurant_address = responses[location]['data']['address']
    except KeyError:
        restaurant_address = None
    try:
        restaurant_neighborhoods = responses[overview]['data']['location']['landmark'].replace('<b>', '').replace('</b>', '')
    except KeyError:
        restaurant_neighborhoods =  None
    try:
        restaurant_website = responses[location]['data']['website']
    except KeyError:
        restaurant_website = None
    try:
        email_id = responses[location]['data']['email']
    except KeyError:
        email_id = None
    try:
        mobile_number = responses[location]['data']['phone']
    except KeyError:
        mobile_number = None
    try:
        restaurant_about = responses[location]['data']['description']
    except KeyError:
        restaurant_about = None
    try:
        price_range = responses[location]['data']['price'],
    except KeyError:
        price_range = None
    try:
        cuisines = ', '.join([i['name'] for i in responses[location]['data']['cuisine']]),
    except KeyError:
        cuisines =None

    image_urls = restaurant_images

    return {
            "restaurant_name": restaurant_name,
            "restaurant_address": restaurant_address,
            "restaurant_neighborhoods": restaurant_neighborhoods,
            "restaurant_website": restaurant_website,
            "email_id": email_id,
            "mobile_number": mobile_number,
            "restaurant_about": restaurant_about,
            "price_range": price_range,
            "cuisines": cuisines,
            "image_urls": image_urls
            }


if __name__ == '__main__':
    print("Scraping Restaurant information.....")
    parser = argparse.ArgumentParser(description='Scrape data from TripAdvisor Restaurant')
    parser.add_argument('-u', '--url', help='Search URL', required=True)

    args = parser.parse_args()
    # url ='https://www.tripadvisor.com/Restaurant_Review-g293924-d6508772-Reviews-Namaste_Hanoi-Hanoi.html'
    print(scrape_restaurant_info(args.url))

