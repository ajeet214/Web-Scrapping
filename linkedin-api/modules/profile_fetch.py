#!/usr/bin/env python
import requests
from credentials import creds
import json
import redis
import time
import re
from selenium import webdriver
from urllib.parse import quote
from bs4 import BeautifulSoup
import multiprocessing
from config import Config
import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, UnableToSetCookieException
from selenium.webdriver.common.keys import Keys
from modules.caps_client import CapsClient, CredentialPlatform, CredentialType
import indicoio
from modules import minio_push


class ProfileFetcher:

    def __init__(self):

        self.c = 0
        credential = CapsClient().get_credential_random(CredentialPlatform.LINKEDIN, CredentialType.COOKIES)

        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        # options.add_argument("--headless")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36")

        if credential['proxy']:
            options.add_argument(
                f"--proxy-server=socks5://{credential['proxy']['host']}:{credential['proxy']['port']}")
        else:
            pass

        # local webdriver
        self.driver = webdriver.Chrome(options=options)

        # remote webdriver
        # self.driver = webdriver.Remote(
        #     command_executor=Config.SELENIUM_URI,
        #     desired_capabilities=options.to_capabilities(),
        # )

        url = "https://www.linkedin.com"

        self.driver.get(url)
        try:
            for cookie in credential['cookies']:
                self.driver.add_cookie(cookie)
        except UnableToSetCookieException as e:
            raise e.msg

    def _get_proxy(self):

        try:
            random_proxy = CapsClient().get_proxy_random(type='socks5')
            print(random_proxy)
            return "socks5://{}:{}".format(random_proxy['host'], random_proxy['port'])

        except:
            return 'socks5://185.121.139.55:21186'
            # '185.20.184.131:3399'

    def data_processor(self, username):

        temp_dict = dict()
        image = self.driver.find_element_by_xpath("//div[@class='ph5 pb5']/div/div[@class='pv-top-card-v3--photo text-align-left']/div/div/img")
        print(image.get_attribute('src'))
        temp_dict['image'] = image.get_attribute('src')
        name = self.driver.find_element_by_xpath("//ul[@class='pv-top-card-v3--list inline-flex align-items-center']/li")
        print(name.text)
        temp_dict['name'] = name.text
        summary = self.driver.find_element_by_xpath("//div[@class='flex-1 mr5']/h2")
        print(summary.text)
        temp_dict['summary'] = summary.text

        location = self.driver.find_element_by_xpath("//div[@class='flex-1 mr5']/ul[2]/li[1]")
        print(location.text)
        temp_dict['location'] = location.text

        connections = self.driver.find_element_by_xpath("//div[@class='flex-1 mr5']/ul[2]/li[2]")
        print(connections.text)
        if 'connections' in connections.text:
            temp_dict['following'] = connections.text
        elif 'followers' in connections.text:
            temp_dict['followers'] = connections.text

        self.driver.switch_to.window(self.driver.window_handles[1])
        # self.driver.get(f'https://www.linkedin.com/in/{username}/detail/contact-info/')

    def scroll_to_bottom(self):

        if self.driver.execute_script("return window.innerHeight") + self.driver.execute_script(
                "return window.scrollY") >= self.driver.execute_script("return document.body.offsetHeight"):
            print("you're at the bottom of the page")
            return False
        else:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            return True

    def profile_fetcher(self, username):

        url = f"https://www.linkedin.com/in/{username}"
        self.driver.get(url)
        self.scroll_to_bottom()

        # soup = BeautifulSoup(self.driver.page_source, 'lxml')
        # print(soup.prettify())
        return self.data_processor(username)


if __name__ == '__main__':
    obj = ProfileFetcher()
    print(obj.profile_fetcher('mathew'))

# harrypotterfans
# thisisbillgates
# yip.kit.hung