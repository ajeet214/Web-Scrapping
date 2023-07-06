"""
Project : Tabelog, Restaurants (Japanese food portal)
Author : Ajeet
Date : July 03, 2023
"""
# import libraries
import os
import argparse
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from config import log, Logging


def scrape_tabelog(url: str) -> Dict:

    log.info('................................Scraping the data from Tabelog................................')
    log.info(f'The URL is : {url}')

    headers = {"User-Agent": Logging.user_agent}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    p_header = soup.select_one('section.rdheader-info-wrap')
    name = soup.select_one('h2.display-name').text.strip()
    # print(name)

    linktree_parent = p_header.select('div.linktree__parent')
    closest_station = linktree_parent[0].text.strip()
    # print(closest_station)

    genre = linktree_parent[2].text.strip()

    try:
        dinner_budget = p_header.select_one('p.rdheader-budget__icon.rdheader-budget__icon--dinner>span.rdheader-budget__price').text.strip()
    except AttributeError:
        dinner_budget = None

    try:
        lunch_budget = p_header.select_one('p.rdheader-budget__icon rdheader-budget__icon--lunch>span.rdheader-budget__price').text
    except AttributeError:
        lunch_budget = None


    closing_days = p_header.select_one('dd#short-comment').text.strip()
    # print(closing_days)


    description_title = soup.select_one('h3.pr-comment-title.js-pr-title').text.strip()
    # print(description_title)
    description = soup.select_one('span.pr-comment__first').text
    # print(description)

    strength_containers = soup.select('div.rstdtl-top-kodawari__modal-textbox')
    strengths = []
    for each_box in strength_containers:
        st_title = each_box.select_one('span.rstdtl-top-kodawari__modal-title').text.strip()
        # print(st_title)
        s_comment = each_box.select_one('p.rstdtl-top-kodawari__modal-comment').text.strip()
        # print(s_comment)
        strengths.append({"strength_title":st_title,
                          "strength_comment": s_comment})

    store_details = {}
    container = soup.select_one('div#rst-data-head')

    t_headers = [i.text.strip() for i in container.select('h4.rstinfo-table__title')]
    # print(t_headers)
    tables = container.select('tbody')
    # print(len(tables))

    for i in range(len(tables)):

        store_details[t_headers[i]] = {}
        rows = tables[i].select('tr')
        for row in rows:
            thead = row.find('th').text.strip()
            tdata = row.find('td').text.strip()
            store_details[t_headers[i]][thead] = tdata

    # print(store_details)

    res2 = requests.get(f'{url}/dtlphotolst/smp2/', headers=headers)
    soup2 = BeautifulSoup(res2.text, 'html.parser')
    images_container = soup2.select('ul.rstdtl-thumb-list.clearfix')[0].select('li.rstdtl-thumb-list__item')

    image_urls = [img.find('img').get('src') for img in images_container]

    if store_details['店舗基本情報']['受賞・選出歴']:
        store_details['店舗基本情報']['受賞・選出歴'] = store_details['店舗基本情報']['受賞・選出歴'].replace('\n\n\n\n\n\n\n', ', ').replace('\n\n\n\n\n', ' ')

    data = {
        "name": name,
        "closest_station": closest_station,
        "genre": genre,
        "dinner_budget": dinner_budget,
        "lunch_budget": lunch_budget,
        "closing_days": closing_days,
        "description_title": description_title,
        "description": description,
        "strengths": strengths,
        "store_details": store_details,
        "image_urls": image_urls,
    }
    log.info(f'scrapped data: \n{data}')
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape data from Tabelog')
    parser.add_argument('-u', '--url', help='Search URL', required=True)

    args = parser.parse_args()
    # 'https://tabelog.com/kyoto/A2601/A260202/26016833'
    scrape_tabelog(args.url)