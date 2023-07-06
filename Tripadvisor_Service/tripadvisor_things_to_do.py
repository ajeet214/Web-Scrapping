"""
Project : Scrape Things to do information from the Tripadvisor
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

def retrieve_restaurant_images(container: element.Tag) -> str:

    l_images = container.select('div.prw_rup.prw_common_basic_image.photo_widget.large.landscape')
    m_images = container.select_one('div.mini_photos_container').select('img')

    all_images = [retrieve_original_image(i.find('img').get('data-lazyurl')) for i in l_images[2:]]+[retrieve_original_image(i.get('data-lazyurl')) for i in m_images]

    return ', '.join(all_images)

def scrape_thigs_to_do_info(url: str):

    response = requests.get(url, headers={"User-Agent": Logging.user_agent})
    soup = BeautifulSoup(response.text, 'html.parser')

    # print(soup.prettify())
    # with open('D:\\automation\\Upwork\\Tripadvisor_Service\\soup_data.html', 'w', encoding='utf-8') as f:
    #     f.writelines(soup.prettify())

    name = soup.select_one('h1[data-automation="mainH1"]').text
    print(name)

    about = soup.find('div', string='About').find_next_sibling('div').text
    print(about)

    website = soup.find()
    # return {
    #         "restaurant_name": restaurant_name,
    #         "restaurant_address": restaurant_address,
    #         "restaurant_neighborhoods": restaurant_neighborhoods,
    #         "restaurant_website": restaurant_website,
    #         "email_id": email_id,
    #         "mobile_number": mobile_number,
    #         "restaurant_about": restaurant_about,
    #         "price_range": price_range,
    #         "cuisines": cuisines,
    #         "image_urls": image_urls
    #         }


if __name__ == '__main__':
    print("Scraping Things to do information.....")
    # url ='https://www.tripadvisor.com.sg/Attraction_Review-g295424-d676922-Reviews-Burj_Khalifa-Dubai_Emirate_of_Dubai.html'
    url ='https://www.tripadvisor.com.sg/Attraction_Review-g295424-d1936354-Reviews-The_Dubai_Fountain-Dubai_Emirate_of_Dubai.html'
    print(scrape_thigs_to_do_info(url))

