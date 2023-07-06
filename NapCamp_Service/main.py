"""
Project : Nap Camp, Camp sites in Japan
Author : Ajeet
Date : July 03, 2023
"""
# import libraries
import os
import argparse
import requests
import json
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from config import log, Logging


def scrape_nap_camp(url: str):

    log.info('................................Scraping the data from Nap Camp................................')
    log.info(f'The URL is : {url}')

    headers = {"User-Agent": Logging.user_agent}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    json_data = json.loads(soup.find('script', type="application/json").text)
    raw_image_urls = [i['imageUrl'] for i in json_data['props']['pageProps']['initialState']['campsite']['data']['images']]
    image_urls = [f"https://mr59fqlw.user.webaccel.jp/img/_image.php?fname={i}&rw=640&wm=resize&rh=500&hm=resize" for i in  raw_image_urls]

    site_name = soup.select_one('h1#gtag-campsite-name').text

    data = {'image_urls': image_urls, 'site_name': site_name}
    site_address = soup.select_one('div[class^="CampsiteDetail_site-address__"]').text.replace('地図を表示', '')
    # print(site_address)
    data['site_address'] = site_address

    site_title = soup.select_one('h2[class^="CampsiteDetail_site-title__"]').text
    # print(site_title)
    data['site_title'] = site_title

    site_details = soup.select_one('div[class^="CampsiteDetail_site-main__"]').text
    # print(site_details)
    data['site_details'] = site_details

    facility_features_container = soup.select_one('ul[class^="CampsiteDetail_charm-content__"]').select('li')
    facility_features = []
    for facility_feature in facility_features_container:
        facility_feature_text = facility_feature.select_one('div[class^="CampsiteDetail_charm-text__"]').text

        facility_features.append({'text': facility_feature_text})

    data['facility_features'] = facility_features

    facility_feature_details = soup.select_one('div[class^="CampsiteDetail_from-content__"]').text
    # print(facility_feature_details)
    data['facility_feature_details'] = facility_feature_details

    containers = soup.select('div[class^="g-container CampsiteDetail_info__"]')

    for container in containers:
        container_title = container.select_one('h3[class^="CampsiteDetail_container-title__"]').text.strip()
        # print(f"{container_title}---------------------------------------------------------------------------")

        if container_title != "体験・遊び・アクティビティ情報":
            table_rows = container.select_one('tbody').select('tr')
            data[container_title] = {}
            for row in table_rows:
                thead = row.find('th').text.strip()
                tdata = row.find('td').text.strip()
                data[container_title][thead] = tdata
        else:
            activities_list = container.select('span[class^="CampsiteDetail_info-table-item___"]')
            data[container_title] = [activity.text for activity in activities_list]


    log.info(f'scrapped data: \n{data}')
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape data from Nap Camp')
    parser.add_argument('-u', '--url', help='Search URL', required=True)

    args = parser.parse_args()
    # https://www.nap-camp.com/nagano/12188
    scrape_nap_camp(args.url)