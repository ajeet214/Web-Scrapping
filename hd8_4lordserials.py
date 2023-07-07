"""
Project : 
Author : Ajeet
Date : July 07, 2023
"""


import json
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")

BASE_URL = 'https://hd8.4lordserials.xyz/anime-serialy'

session = requests.Session()
session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'

items = []
def scrape_page(url: str) -> None:
    """
    Scrape data from a specific page URL.

    Args:
        url (str): The URL of the page to scrape.

    Returns:
        None

    Raises:
        requests.HTTPError: If the HTTP request to the page fails.
    """
    rs = session.get(url, verify=False)
    rs.raise_for_status()
    soup = BeautifulSoup(rs.content, 'html.parser')

    for item in soup.select('.th-item'):
        title = item.select_one('.th-title').text
        url = item.a['href']
        items.append({
            'title': title,
            'url': url,
        })

def scrape_all_pages(base_url: str) -> None:
    """
    Scrape data from all pages of the provided base URL.

    Args:
        base_url (str): The base URL to scrape data from.

    Returns:
        None
    """
    response = session.get(base_url, verify=False).text
    soup = BeautifulSoup(response, 'html.parser')
    max_page = int(soup.select('div.navigation>a')[-1].text)
    print(f"maximum pages: {max_page}")

    for page in range(1, max_page + 1):
        page_url = f'{base_url}/page/{page}/'
        print(f"page url: {page_url}")
        scrape_page(page_url)


if __name__ == '__main__':

    scrape_all_pages(BASE_URL)
    print(f"total items: {len(items)}")
    with open('out.json', 'w', encoding='utf-8') as f:
        json.dump(items, f, indent=4, ensure_ascii=False)

    """
    After scraping all the pages, the code prints the total number of items collected and saves the data as a JSON file 
    named "out.json" with proper indentation and encoding.

    maximum pages: 21
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/1/
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/2/
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/3/
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/4/
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/5/
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/6/
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/7/
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/8/
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/9/
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/10/
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/11/
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/12/
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/13/
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/14/
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/15/
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/16/
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/17/
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/18/
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/19/
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/20/
    page url: https://hd8.4lordserials.xyz/anime-serialy/page/21/
    total items: 497

    reference: https://stackoverflow.com/questions/76634668/automatic-pages-switch-on-python
    """

