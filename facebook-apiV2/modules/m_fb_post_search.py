import json
from time import sleep
import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import urllib.parse
from credential import creds

import demjson


class PostSearch:

    def __init__(self):
        
        self.Cookies = json.loads(creds['m_cookies'])
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extension")
        prefs = {"profile.default_content_setting_values.notifications": 2}
        options.add_experimental_option("prefs", prefs)

        # options.add_argument("--headless")
        self.driver = webdriver.Chrome(chrome_options=options)

        url = "http://m.facebook.com"

        start_time = time.time()
        self.driver.get(url)

        for cookie in self.Cookies:
            cookie_dict = {'domain': None, 'secure': cookie['secure'], 'value': cookie['value'],
                           'name': cookie['name'], 'httpOnly': cookie['httpOnly'], 'storeId': cookie['storeId'],
                           'path': cookie['path'], 'session': cookie['session'], 'hostOnly': cookie['hostOnly'],
                           'sameSite': cookie['sameSite'], 'id': cookie['id']}
            try:
                if cookie['expirationDate']:
                    cookie_dict['expirationDate'] = cookie['expirationDate']
                    # print(cookie['expirationDate'])
            except:
                pass
            # print(cookie_dict)
            self.driver.add_cookie(cookie_dict)

    def fb_posts(self, query):

        query = urllib.parse.quote(query)
        self.driver.get('https://m.facebook.com/search/posts/?q={}&source=filter&isTrending=0'.format(query))
        sleep(0.5)

        try:
            self.driver.find_element_by_xpath('//*[@id="xt_uniq_6"]').click()
            sleep(0.5)

            #
            for i in range(15):
                self.driver.execute_script("window.scrollTo(0, 19440)")
                sleep(1)

            return  self.data_processor()

        # When there are very few posts
        except NoSuchElementException:
            return self.data_processor()

    def data_processor(self):
        lst = []

        content = self.driver.page_source
        self.driver.close()

        count = 0
        print(BeautifulSoup(content, 'html.parser').prettify())
        # posts = driver.find_elements_by_class_name("_5bl2 _3u1 _41je")
        data = BeautifulSoup(content, 'html.parser')

        container = data.find_all('div', id="BrowseResultsContainer")
        print(len(container))
        for i in container:

            for j in i.find_all('div', class_="_a5o _9_7 _2rgt _1j-f _2rgt")[::2]:
                temp_dict = dict()
                # header includes author_image, author_name, datetime and verified status
                header = j.find('div', class_='_a58 _9_7 _2rgt _1j-g _2rgt')

                author_image = header.find('div', class_='_9_7 _2rgt _1j-g _2rgt').img['src']
                temp_dict['author_image'] = author_image

                try:
                    verified = header.find('div', class_='_a5o _9_7 _2rgt _1j-f _2rgt').find(
                        'div', class_='_9_7 _2rgt _1j-g _2rgt').find('span').img['src']
                    verified = True
                except AttributeError:
                    verified = False

                temp_dict['verified'] = verified

                # print(header.text)

                author_name = header.text.split('·')[0]
                temp_dict['author_name'] = author_name
                datetime = header.text.split('·')[1]
                temp_dict['datetime'] = datetime

                post_data = j.find('div', class_='_a58 _a5v _9_7 _2rgt _1j-f _2rgt')

                try:
                    thumbnail = post_data.find('img')['src']
                except TypeError:
                    thumbnail = None

                temp_dict['thumbnail'] = thumbnail

                # number of likes, shares and comments
                reactions = j.find('div', class_='_2nx_ _2rgt _1j-g _2rgt')
                likes = reactions.find('div', class_='_1g06').text
                temp_dict['likes'] = likes
                comments_and_shares = reactions.find('div', class_='_1fnt').text.split('comments')
                temp_dict['comments'] = comments_and_shares[0].replace(' ', '')
                try:
                    temp_dict['shares'] = comments_and_shares[1].replace(' shares', '')
                except IndexError:
                    temp_dict['shares'] = 0
                lst.append(temp_dict)
                # print(j.text)

                count += 1

        print(count)
        return lst


if __name__ == '__main__':
    obj = PostSearch()
    print(obj.fb_posts('trump'))
