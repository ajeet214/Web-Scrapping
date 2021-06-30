import json
from urllib.parse import unquote
from time import sleep
import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import urllib.parse
from credential import creds
import re
import datetime
import demjson
from config import Config


class PostSearch:

    def __init__(self):

        self.Cookies = json.loads(creds['cookies'])
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extension")
        prefs = {"profile.default_content_setting_values.notifications": 2}
        options.add_experimental_option("prefs", prefs)

        # options.add_argument("--headless")
        # self.driver = webdriver.Chrome(options=options)

        # remote webdriver
        self.driver = webdriver.Remote(
            command_executor='http://' + Config.SELENIUM_CONFIG['host'] + ':' + Config.SELENIUM_CONFIG[
                'port'] + '/wd/hub',
            desired_capabilities=options.to_capabilities(),
        )

        url = "http://www.facebook.com"

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
        self.driver.get('https://www.facebook.com/search/posts/?q={}&epa=SERP_TAB'.format(query))
        sleep(0.2)

        self.driver.find_element_by_link_text('Public').click()
        sleep(0.1)

        for i in range(30):

            self.driver.execute_script("window.scrollTo(0, 20520)")
            sleep(1)

        return self.data_processor()

    def data_processor(self):

        lst = []
        content = self.driver.page_source
        sleep(0.2)
        self.driver.close()

        # print(BeautifulSoup(content, 'html.parser').prettify())
        soup = BeautifulSoup(content, 'html.parser')
        posts = soup.find_all('div', class_="_6rbb")

        for each_section in posts:

            for i in each_section.find_all('div', class_='_6-e5 _401d'):
                temp_dict = dict()

                header = i.find('div', class_='_6-e6')
                try:
                    print(header.find(class_='_6-cn').find('span')['data-hover'])
                except:
                    pass
                # try:
                #     header.find(class_='_6-cn').find('span', class_='class="_56_f _5dzy _5dz- _3twv"')
                #     temp_dict['verified'] = True
                #
                # except:
                #     temp_dict['verified'] = False

                content = i.find('div', class_='_6-co')
                reactions_comments_shares = i.find('div', class_='_6-cy')
                try:
                    reactions = reactions_comments_shares.find('span', class_="_3dlh _3dli").text
                    temp_dict['likes'] = reactions
                    if 'K' in temp_dict['likes']:
                        temp_dict['likes'] = float(temp_dict['likes'].replace('K', ''))*1000
                    elif 'M' in temp_dict['likes']:
                        temp_dict['likes'] = float(temp_dict['likes'].replace('M', '')) * 1000000
                    else:
                        temp_dict['likes'] = int(temp_dict['likes'])

                except ValueError:
                    print(reactions_comments_shares.find('span', class_="_3dlh _3dli").text)
                    # print(re.sub("\D", "", reactions_comments_shares.find('span', class_="_3dlh _3dli").text))
                except AttributeError:
                    temp_dict['likes'] = 0

                comments_shares = reactions_comments_shares.find('div', class_="_78k7").text
                # print(comments_shares)
                # when there is no comment and share
                if not comments_shares:
                    temp_dict['comments'] = 0
                    temp_dict['shares'] = 0
                # when there is either comments or shares or both
                else:
                    # when there is only comment
                    if comments_shares.endswith('comment') or comments_shares.endswith('comments'):
                        # print(comments_shares)
                        temp_dict['comments'] = comments_shares.replace('comments', '').replace('comment', '').replace(' ', '')
                        # print(temp_dict['comments'])

                        if 'K' in temp_dict['comments']:
                            temp_dict['comments'] = float(temp_dict['comments'].replace('K', ''))*1000
                        elif 'M' in temp_dict['comments']:
                            temp_dict['comments'] = float(temp_dict['comments'].replace('M', '')) * 1000000

                        # print(temp_dict['comments'])
                        temp_dict['comments'] = int(temp_dict['comments'])
                        temp_dict['shares'] = 0

                    # when there is only share
                    elif comments_shares.find('comment') == -1:
                        print(comments_shares)
                        temp_dict['shares'] = comments_shares.replace('shares', '').replace('share', '').replace(' ', '')
                        if 'K' in temp_dict['shares']:
                            temp_dict['shares'] = float(temp_dict['shares'].replace('K', '')) * 1000
                        elif 'M' in temp_dict['shares']:
                            temp_dict['shares'] = float(temp_dict['shares'].replace('M', '')) * 1000000

                        temp_dict['shares'] = int(temp_dict['shares'])
                        temp_dict['comments'] = 0

                    # when there is both
                    else:
                        list_of_comments_and_shares = comments_shares.replace('comments', '-').replace(
                            'comment', '-').replace('shares', '-').replace('share', '-').split('-')

                        # processing of comments and shares
                        temp_dict['comments'] = list_of_comments_and_shares[0].replace(' ', '')
                        if 'K' in temp_dict['comments']:
                            temp_dict['comments'] = float(temp_dict['comments'].replace('K', ''))*1000
                        elif 'M' in temp_dict['comments']:
                            temp_dict['comments'] = float(temp_dict['comments'].replace('M', '')) * 1000000
                        else:
                            temp_dict['comments'] = int(temp_dict['comments'])

                        temp_dict['comments'] = int(temp_dict['comments'])

                        temp_dict['shares'] = list_of_comments_and_shares[1].replace(' ', '')
                        if 'K' in temp_dict['shares']:
                            temp_dict['shares'] = float(temp_dict['shares'].replace('K', ''))*1000
                        elif 'M' in temp_dict['shares']:
                            temp_dict['shares'] = float(temp_dict['shares'].replace('M', '')) * 1000000

                        else:
                            # print(temp_dict['shares'])
                            temp_dict['shares'] = int(temp_dict['shares'])

                        temp_dict['shares'] = int(temp_dict['shares'])

                # ------------------------------

                try:
                    temp_dict['thumbnail'] = content.img['src']
                    temp_dict['type'] = 'image'

                except TypeError:
                    temp_dict['thumbnail'] = None
                    temp_dict['type'] = "status"

                try:
                    if '/videos/' in content.find('div', class_='_6-cr _6-cv').find('a')['href']:
                        temp_dict['type'] = 'video'
                except:
                    pass
                #     # print(content.find('div', class_='_6-cr _6-cv').find('a')['href'])
                #     if content.find('div', class_='_6-cr _6-cv').find('img'):
                #         temp_dict['type'] = 'image'
                #
                #     elif '/photos/' in content.find('div', class_='_6-cr _6-cv').find('a')['href']:
                #         temp_dict['type'] = 'image'
                #

                #
                # except AttributeError:
                #     try:
                #         print(content.find('div', class_='_6-cr _6-cw').find('a')['href'])
                #         temp_dict['type'] = 'image'
                #     except AttributeError:
                #         print(content.find('div', class_='_6-cr _6-cx').find('a')['href'])
                #         temp_dict['type'] = 'image'
                # except TypeError:
                #     pass

                temp_dict['url'] = 'https://www.facebook.com'+content.find('span', class_='_6-cm').a['href']
                if '/videos' in temp_dict['url']:
                    temp_dict['type'] = 'video'
                temp_dict['datetime'] = content.find('span', class_='_6-cm').a.text
                temp_dict['content'] = content.text.replace(content.find('span', class_='_6-cm').text, '')
                temp_dict['content'] = unquote(temp_dict['content'])

                temp_dict['author_image'] = header.find('img')['src']
                temp_dict['author_name'] = header.find('div', class_='_6-cn').text
                # temp_dict['url'] = header.find('div', class_='_6-cn').a['href']
                temp_dict['author_userid'] = header.find('div', class_='_6-cn').a['href'].split('/')[3]

                if type(temp_dict['likes']) == str:
                    temp_dict['likes'] = re.sub("\D", "", temp_dict['likes'])

                elif not temp_dict['likes']:
                    temp_dict['likes'] = 0
                temp_dict['likes'] = int(temp_dict['likes'])

                if 'hrs' in temp_dict['datetime'] or 'hr' in temp_dict['datetime']:
                    post_time = datetime.datetime.now() - datetime.timedelta(
                        hours=int(temp_dict['datetime'].lstrip()[0:2]))
                    post_time = post_time.strftime('%Y-%m-%d %H:%M:%S')

                    # Convert from human readable date to epoch
                    # int(time.mktime(time.strptime('2000-01-01 12:34:00', '%Y-%m-%d %H:%M:%S'))) - time.timezone
                    temp_dict['datetime'] = int(
                        time.mktime(time.strptime(post_time, '%Y-%m-%d %H:%M:%S'))) - time.timezone

                elif 'mins' in temp_dict['datetime']:
                    post_time = datetime.datetime.now()-datetime.timedelta(minutes=int(temp_dict['datetime'].lstrip()[0:2]))
                    post_time = post_time.strftime('%Y-%m-%d %H:%M:%S')

                    # Convert from human readable date to epoch
                    temp_dict['datetime'] = int(time.mktime(time.strptime(post_time, '%Y-%m-%d %H:%M:%S'))) - time.timezone

                elif 'Yesterday' in temp_dict['datetime']:
                    g = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y %m %d')
                    temp_dict['datetime'] = int(datetime.datetime.strptime(g, '%Y %m %d').timestamp())

                else:
                    try:
                        temp_dict['datetime'] = int(
                            datetime.datetime.strptime(temp_dict['datetime'].lstrip(), '%d %b %Y').timestamp())
                    except ValueError:
                        temp_dict['datetime'] = temp_dict['datetime']+' ' + str(datetime.datetime.now().year)
                        temp_dict['datetime'] = int(
                            datetime.datetime.strptime(temp_dict['datetime'].lstrip(), '%d %b %Y').timestamp())

                lst.append(temp_dict)
                # print(i.text)
                # print('****')

        # print(count)
        return lst


if __name__ == '__main__':
    obj = PostSearch()
    print(obj.fb_posts('Nguyễn Phú Trọng'))
