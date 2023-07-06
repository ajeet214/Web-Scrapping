"""
Project : TripAdvisor, extract all the urls from restaurants, hotels and things to do based on the search query.
Author : Ajeet
Date : July 02, 2023
"""
# import libraries
import os
import argparse
from typing import List, Dict, Optional
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from config import log_url_config, Logging
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

log = log_url_config()

class TripAdvisor:

    def __init__(self):

        options = ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--headless')
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_argument(f"--user-agent={Logging.user_agent}")
        self.driver = Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 10)

    @staticmethod
    def data_processing(results: List) -> List[str]:

        result_link_list = []
        for result in results:
            # print(restaurant.find_element(By.CSS_SELECTOR, 'div.result-title').text)
            partial_link = result.find_element(By.CSS_SELECTOR, 'div.result-title').get_attribute('onclick').split(',')[3].strip().replace("'", "")
            result_link = f"https://www.tripadvisor.com{partial_link}"
            result_link_list.append(result_link)

        return result_link_list


    def page_search(self, url: str) -> List[str]:

        self.driver.get(url)

        restaurants = self.wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.ui_columns.is-mobile.result-content-columns')))

        return self.data_processing(restaurants)

    @staticmethod
    def select_language(lang):

        if lang in ['ca', 'cl', 'co', 'it', 'es', 'de', 'fr', 'se', 'nl', 'dk', 'ie', 'at', 'pt', 'ru', 'ch', 'be',
                        'jp', 'cn', 'in']:
            return f"https://www.tripadvisor.{lang}"

        elif lang in ['br', 'mx', 'ar', 'pe', 've', 'tr', 'gr', 'au', 'my', 'ph', 'sg', 'vn', 'tw', 'hk', 'eg']:
            return f"https://www.tripadvisor.com.{lang}"

        elif lang in ['uk', 'nz', 'id', 'kr', 'za', 'il']:
            return f"https://www.tripadvisor.co.{lang}"

        elif lang in ['cn', 'ar', 'th', 'no']:
            return f"https://{lang}.tripadvisor.com"

    def get_all_pages_urls(self, query, category, language=None):
        total_data = None
        search_url = None

        if language is None:
            base_url = 'https://www.tripadvisor.com'
        else:
            base_url = self.select_language(language)

        if category == 'r':
            search_url = f"{base_url}/Search?q={query}&ssrc=e"
            log.info(f"searching for restaurants in {query} .........")
            print(f"searching for restaurants in {query} .........")
            log.info("getting the restaurant urls from page 1")
            print("getting the restaurant urls from page 1")
            total_data = self.page_search(search_url)

        elif category == 'h':
            search_url = f"{base_url}/Search?q={query}&ssrc=h"
            log.info(f"searching for hotels in {query} .........")
            print(f"searching for hotels in {query} .........")
            log.info("getting the hotel urls from page 1")
            print("getting the hotel urls from page 1")
            total_data = self.page_search(search_url)

        elif category == 't':
            search_url = f"{base_url}/Search?q={query}&ssrc=A"
            log.info(f"searching for things to do in {query} .........")
            print(f"searching for things to do in {query} .........")
            log.info("getting the things to do urls from page 1")
            print("getting the things to do urls from page 1")
            total_data = self.page_search(search_url)


        total_pages = self.wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.pageNumbers > a')))[-1].text

        log.info(f"total number of pages: {total_pages}")
        print(f"total number of pages: {total_pages}")

        for i, n in enumerate(range(30, int(total_pages)*30, 30), start=2):
            log.info(f"getting the restaurant urls from page {i}")
            print(f"getting the restaurant urls from page {i}")
            total_data.extend(self.page_search(f"{search_url}&o={n}"))

        log.info(f"total restaurant urls scrapped: {len(total_data)}")
        print(f"total restaurant urls scrapped: {len(total_data)}")
        return total_data

        # self.driver.find_element(By.CSS_SELECTOR, 'button[aria-haspopup="menu"]').click()
        # time.sleep(2)
        # langs = self.driver.find_elements(By.CSS_SELECTOR, 'li[role="none"]>a')
        # for l in langs:
        #     print(l.get_attribute('href'))

    def save_data(self, query: str, category: str, language=None, path: Optional[str] = os.getcwd()) -> None:
        """ save the data to a CSV file at the given path.

        Args:
        query: the query to search
        category: the category to search for.
        language: search language, default is english(None)
        path: the path to save the file (the default is os.getcwd(), which saves the file in the current directory)

        Returns: None
        """
        filename = None
        if category == 'r':
            filename = 'restaurant'

        elif category == 'h':
            filename = 'hotel'

        elif category == 't':
            filename = 'things_to_do'

        data = self.get_all_pages_urls(query, category, language)
        df = pd.DataFrame({f"{filename}_url": data})
        file_location = f'{path}/{filename}_urls.csv'

        df.to_csv(file_location, index=False)
        log.info(f"------------data is saved at {file_location}------------")
        print(f"------------data is saved at {file_location}------------")


if __name__ == '__main__':

    obj = TripAdvisor()
    parser = argparse.ArgumentParser(description='Scrape URLs from search Query and chosen Category')
    parser.add_argument('-q', '--query', help='Search query', required=True)
    parser.add_argument('-c', '--category', help='category to search from', required=True)
    parser.add_argument('-l', '--language', help='search language', required=False)
    args = parser.parse_args()
    # print(args.query)

    obj.save_data(args.query, args.category)

    # run the below command on the terminal to search for things to do in tokyo,japan:
    # python main.py -q tokyo,japan -c t
