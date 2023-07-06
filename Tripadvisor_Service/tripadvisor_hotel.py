"""
Project : Scrape Hotel information from the Tripadvisor
Author : Ajeet
Date : July 02, 2023
"""
import re
import requests
import json
from typing import Dict
from bs4 import BeautifulSoup, element
from config import Logging


def retrieve_original_image(img: str) -> str:
    return img.replace('photo-s', 'photo-o').replace('photo-f', 'photo-o').replace('photo-t', 'photo-o').replace('photo-l', 'photo-o')

def retrieve_hotel_images(container: element.Tag) -> str:

    l_images = container.select('div.prw_rup.prw_common_basic_image.photo_widget.large.landscape')
    m_images = container.select_one('div.mini_photos_container').select('img')

    all_images = [retrieve_original_image(i.find('img').get('data-lazyurl')) for i in l_images[2:]]+[retrieve_original_image(i.get('data-lazyurl')) for i in m_images]

    return ', '.join(all_images)

def scrape_hotel_info(url: str) -> Dict:

    response = requests.get(url, headers={"User-Agent": Logging.user_agent})
    soup = BeautifulSoup(response.text, 'html.parser')

    # image_container = soup.select_one('div.mosaic_photos')
    # hotel_images = retrieve_hotel_images(image_container)
    #
    pattern = r'<script>\s+window.__WEB_CONTEXT__=(.+);\(this\.\$WP=this\.\$WP\|\|\[\]\)'
    script_data = re.search(pattern=pattern, string=soup.prettify())

    json_data = json.loads(script_data[1].replace("pageManifest", '"pageManifest"'))

    responses = json_data['pageManifest']['urqlCache']['results']
    print(responses)
    # location = re.search(pattern=r'/data/[0-9.]+/location/\d+', string=str(responses)).group()
    #
    # overview = re.search(pattern=r'/data/[0-9.]+/hotel/\d+/overview', string=str(responses)).group()
    #
    #
    hotel_name = soup.select_one('h1#HEADING').text
    print(hotel_name)

    # hotel_address = soup.select_one()
    # try:
    #     hotel_address = responses[location]['data']['address']
    # except KeyError:
    #     hotel_address = None
    # try:
    #     hotel_neighborhoods = responses[overview]['data']['location']['landmark'].replace('<b>', '').replace('</b>', '')
    # except KeyError:
    #     hotel_neighborhoods =  None
    # try:
    #     hotel_website = responses[location]['data']['website']
    # except KeyError:
    #     hotel_website = None
    # try:
    #     email_id = responses[location]['data']['email']
    # except KeyError:
    #     email_id = None
    # try:
    #     mobile_number = responses[location]['data']['phone']
    # except KeyError:
    #     mobile_number = None
    # try:
    #     hotel_about = responses[location]['data']['description']
    # except KeyError:
    #     hotel_about = None
    # try:
    #     price_range = responses[location]['data']['price'],
    # except KeyError:
    #     price_range = None
    # try:
    #     cuisines = ', '.join([i['name'] for i in responses[location]['data']['cuisine']]),
    # except KeyError:
    #     cuisines =None
    #
    # image_urls = hotel_images
    #
    # return {
    #         "hotel_name": hotel_name,
    #         "hotel_address": hotel_address,
    #         "hotel_neighborhoods": hotel_neighborhoods,
    #         "hotel_website": hotel_website,
    #         "email_id": email_id,
    #         "mobile_number": mobile_number,
    #         "hotel_about": hotel_about,
    #         "price_range": price_range,
    #         "cuisines": cuisines,
    #         "image_urls": image_urls
    #         }


if __name__ == '__main__':
    print("Scraping hotel information.....")
    # url = 'https://www.tripadvisor.com/Hotel_Review-g293924-d2304786-Reviews-Hanoi_Sky_Hotel-Hanoi.html'
    url = 'https://www.tripadvisor.com/Hotel_Review-g295424-d2026811-Reviews-Howard_Johnson_by_Wyndham_Bur_Dubai-Dubai_Emirate_of_Dubai.html'
    print(scrape_hotel_info(url))

# urls = ['https://www.tripadvisor.com/Hotel_Review-g293924-d2304786-Reviews-Hanoi_Sky_Hotel-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d8536265-Reviews-Hanoi_Peridot_Hotel-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d615317-Reviews-La_Siesta_Premium_Hang_Be-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d2298266-Reviews-AIRA_Boutique_Hanoi_Hotel_Spa-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d7180030-Reviews-La_Siesta_Classic_Ma_May-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d5049935-Reviews-Lotte_Hotel_Hanoi-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d17415144-Reviews-The_Oriental_Jade_Hotel-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d299548-Reviews-Sofitel_Legend_Metropole_Hanoi-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d299586-Reviews-Pan_Pacific_Hanoi-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d1592633-Reviews-Silk_Path_Hotel_Hanoi-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d9786699-Reviews-Hanoi_Marvellous_Hotel_Spa-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d10550496-Reviews-O_Gallery_Premier_Hotel_Spa-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d13507503-Reviews-JM_Marvel_Hotel_Spa-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d1533551-Reviews-Sheraton_Hanoi_Hotel-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d4042083-Reviews-JW_Marriott_Hotel_Hanoi-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d8615276-Reviews-Silk_Path_Boutique_Hanoi-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d9808263-Reviews-Bespoke_Trendy_Hotel_Hanoi-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d4609521-Reviews-Hanoi_Pearl_Hotel-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d588636-Reviews-Hanoi_House_Hostel_Travel-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d943311-Reviews-Oriental_Suites_Hotel_Spa-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d1224737-Reviews-La_Nueva_Boutique_Hotel_Hanoi-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d4993403-Reviews-Hanoi_Royal_Palace_Hotel_2-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d1638735-Reviews-Hanoi_Impressive_Hotel-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d1950147-Reviews-Hotel_de_l_Opera_Hanoi-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d1546077-Reviews-Splendid_Star_Grand_Hotel-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d301984-Reviews-Hilton_Hanoi_Opera-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d2102670-Reviews-Luxury_Backpackers_Hanoi-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d17627438-Reviews-La_Sinfonia_del_Rey_Hotel_Spa-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d7392141-Reviews-Apricot_Hotel-Hanoi.html', 'https://www.tripadvisor.com/Hotel_Review-g293924-d2328401-Reviews-Hanoi_Media_Hotel_Spa-Hanoi.html']

