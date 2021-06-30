# from urllib.parse import urlencode, unquote
from bs4 import BeautifulSoup
import asyncio
import multiprocessing
# import base64
import json
import redis
import datetime
import time
import indicoio
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from config import Config
from modules import minio_push
from modules.caps_client import CapsClient


class GoogleNews:

    def __init__(self):

        indicoio.config.api_key = CapsClient().get_credential_random('indico', 'api_key')['api_key']['access_token']
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extension")
        options.add_argument("--proxy-server={}".format(self._get_proxy()))
        # options.add_argument("--proxy-server=socks5://176.107.177.59:3388")

        # local webdriver
        # self.driver = webdriver.Chrome(options=options)

        # remote webdriver
        self.driver = webdriver.Remote(
            command_executor=Config.SELENIUM_URI,
            desired_capabilities=options.to_capabilities(),
        )

        url = 'https://www.google.com/ncr'
        self.driver.get(url)

    # random proxy based on chosen filters
    def _get_proxy(self):

        try:
            random_proxy = CapsClient().get_proxy_random(type='socks5')
            print(random_proxy)
            return "socks5://{}:{}".format(random_proxy['host'], random_proxy['port'])

        except:
            return 'socks5://45.76.44.175:4899'

    def indico_sentiment(self, data):

        pol = indicoio.sentiment(data)
        if pol > 0.7000000000000000:
            return "positive"
        elif pol < 0.3000000000000000:
            return "negative"
        else:
            return "neutral"

    def redis_channel(self, selenium_session):

        # r = redis.Redis(host=self.redis_host, port=self.redis_port)
        r = redis.from_url("redis://{}".format(Config.REDIS_URI))
        client_id = 'google_news_service_' + selenium_session
        p = r.pubsub()  # pubsub object
        p.subscribe(client_id)
        return client_id, r, p

    def parser(self, html_data, client_id, redis_obj):

        soup1 = BeautifulSoup(html_data, 'lxml').find('div', id="search")
        for j in soup1.find_all('div', class_="g"):

            temp_dict = dict()

            temp_dict['title'] = j.h3.text
            temp_dict['url'] = j.h3.a['href']

            # try:
            #     temp_dict['thumbnail'] = j.img['src']
            # except TypeError:
            #     temp_dict['thumbnail'] = None

            try:
                image_url = j.img['src']
                minio_url = minio_push.start_uploading([image_url], 'google-service')
                for i in minio_url:
                    if i['status'] == 200:
                        temp_dict['thumbnail'] = i['file_url']
                    else:
                        raise Exception('image not found')
            except:
                temp_dict['thumbnail'] = None

            des = j.find('div', class_='st').text
            temp_dict['content'] = des

            source_and_time = j.find('div', class_='slp')
            temp_list = []
            for i in source_and_time.find_all('span'):
                temp_list.append(i.text)

            temp_dict['source'] = temp_list[0]
            temp_dict['datetime'] = temp_list[2].replace(',', '')

            if 'hour' in temp_dict['datetime']:
                post_time = datetime.datetime.now() - datetime.timedelta(hours=int(temp_dict['datetime'].lstrip()[0:2]))
                post_time = post_time.strftime('%Y-%m-%d %H:%M:%S')

                # Convert from human readable date to epoch
                # int(time.mktime(time.strptime('2000-01-01 12:34:00', '%Y-%m-%d %H:%M:%S'))) - time.timezone
                temp_dict['datetime'] = int(time.mktime(time.strptime(post_time, '%Y-%m-%d %H:%M:%S'))) - time.timezone

            elif 'minute' in temp_dict['datetime']:
                post_time = datetime.datetime.now() - datetime.timedelta(
                    minutes=int(temp_dict['datetime'].lstrip()[0:2]))
                post_time = post_time.strftime('%Y-%m-%d %H:%M:%S')

                # Convert from human readable date to epoch
                temp_dict['datetime'] = int(time.mktime(time.strptime(post_time, '%Y-%m-%d %H:%M:%S'))) - time.timezone

            elif 'day' in temp_dict['datetime']:
                post_time = datetime.datetime.now() - datetime.timedelta(days=int(temp_dict['datetime'].lstrip()[0:2]))
                post_time = post_time.strftime('%Y-%m-%d %H:%M:%S')

                # Convert from human readable date to epoch
                temp_dict['datetime'] = int(time.mktime(time.strptime(post_time, '%Y-%m-%d %H:%M:%S'))) - time.timezone

            elif temp_dict['datetime'].istitle():
                try:
                    temp_dict['datetime'] = int(
                        datetime.datetime.strptime(temp_dict['datetime'].lstrip(), '%d %b %Y').timestamp())
                except ValueError:
                    temp_dict['datetime'] = int(
                        datetime.datetime.strptime(temp_dict['datetime'].lstrip(), '%b %d %Y').timestamp())

            else:
                temp_dict['datetime'] = int(
                    datetime.datetime.strptime(temp_dict['datetime'].lstrip(), '%b %d %Y').timestamp())

            temp_dict['polarity'] = self.indico_sentiment(temp_dict['content'])

            if not temp_dict['content']:
                temp_dict['content'] = None

            temp_dict['type'] = 'news'

            print(temp_dict)
            redis_obj.publish(client_id, json.dumps(temp_dict))
            # final_list.append(temp_dict)
        return

    def pagination(self, client_id, redis_obj, channel_obj):

        count = 0
        condition = True
        while condition:

            try:
                count += 1
                html_data = self.driver.page_source
                self.parser(html_data, client_id, redis_obj)
                sleep(2)
                self.driver.find_element_by_link_text('Next').click()

                if count == 20:
                    condition = False
                    redis_obj.publish(client_id, 'EOF')
                    channel_obj.unsubscribe(client_id)
                    self.driver.quit()

                sleep(1)

            except Exception as e:
                print(e)
                condition = False
                redis_obj.publish(client_id, 'EOF')
                channel_obj.unsubscribe(client_id)
                self.driver.quit()

    def get(self, query, time_duration=None, from_date=None, to_date=None):

        print("query: ", query)

        # q = self.driver.find_element_by_xpath('//*[@id="tsf"]/div[2]/div/div[1]/div/div[1]/input')
        q = self.driver.find_element_by_xpath("//input[@name='q']")
        q.send_keys(query)
        q.send_keys(Keys.ENTER)
        sleep(1)

        try:
            self.driver.find_element_by_class_name('logo')

            # when date filter is chosenk
            if time_duration:
                self.driver.find_element_by_xpath('//*[@id="hdtb-tls"]').click()
                sleep(0.5)
                self.driver.find_element_by_xpath('//*[@id="hdtbMenus"]/div/div[2]').click()
                sleep(0.5)
                if time_duration == 'past_day':
                    self.driver.find_element_by_xpath('//*[@id="qdr_d"]').click()
                elif time_duration == 'past_week':
                    self.driver.find_element_by_xpath('//*[@id="qdr_w"]').click()
                elif time_duration == 'past_month':
                    self.driver.find_element_by_xpath('//*[@id="qdr_m"]').click()
                elif time_duration == 'past_year':
                    self.driver.find_element_by_xpath('//*[@id="qdr_m"]').click()

            else:
                if from_date or to_date:
                    self.driver.find_element_by_xpath('//*[@id="hdtb-tls"]').click()
                    sleep(0.5)
                    self.driver.find_element_by_xpath('//*[@id="hdtbMenus"]/div/div[2]').click()
                    sleep(0.5)

                    self.driver.find_element_by_xpath('//span[@id="cdrlnk"]').click()
                    if from_date:
                        readable_date = time.strftime("%m/%d/%Y", time.localtime(from_date))
                        self.driver.find_element_by_xpath('//form/input[@id="cdr_min"]').send_keys(readable_date)

                    if to_date:
                        readable_date = time.strftime("%m/%d/%Y", time.localtime(to_date))
                        self.driver.find_element_by_xpath('//form/input[@id="cdr_max"]').send_keys(readable_date)

                    self.driver.find_element_by_xpath('//div[@id="cdr_cont"]/div[2]/div[3]/form/input[@value="Go"]').click()

            try:
                self.driver.find_element_by_xpath("//div[@id='search']/div")

                try:
                    # click on news tab
                    # self.driver.find_element_by_xpath('//*[@id="hdtb-msb-vis"]/div[2]/a').click()
                    sleep(0.5)
                    self.driver.find_element_by_link_text('News').click()
                    sleep(0.5)
                    self.driver.find_element_by_xpath("//div[@id='search']/div")

                    selenium_session_id = self.driver.session_id
                    client_id, redis_obj, channel_obj = self.redis_channel(selenium_session_id)

                    # t = threading.Thread(target=self.get_posts, args=(self.driver, client_id, redis_obj, channel_obj))
                    t = multiprocessing.Process(target=self.pagination, args=(client_id, redis_obj, channel_obj))
                    t.start()

                    return {"channel_id": client_id}
                except NoSuchElementException as e:
                    print(e.msg, '**')
                    self.driver.quit()
                    return {"message": "no data found"}
            except NoSuchElementException as e:
                print(e.msg, '*')
                self.driver.quit()
                return {"message": "no data found"}

        except NoSuchElementException as e:
            print(e.msg)
            self.driver.quit()
            return {"message": "captcha detected"}

    # processing query based on the given filters
    def processor(self, q=None, filetype=None, site=None, time_duration=None,
                  exclude=None, intitle=None, from_date=None, to_date=None):

        # query filters
        query = ''
        if q:
            query += f'"{q}"'
        if exclude:
            query += f' -{exclude}'
        if intitle:
            query += f' intitle:{intitle}'
        if site:
            query += f' site:{site}'
        if filetype:
            query += f' filetype:{filetype}'

        list_res = self.get(query, time_duration, from_date, to_date)
        # print(list_res)
        return list_res


if __name__ == '__main__':
    obj = GoogleNews()
    # print(obj.processor(q='donald', exclude='trump', intitle="forbes", filetype='doc', site:'forbes.com', time_duration='past_day', from_date=1558322834, to_date=1558522834))
    print(obj.processor(q='donald', exclude='trump', site='forbes.com', to_date=1555322834))

# erica freymond
