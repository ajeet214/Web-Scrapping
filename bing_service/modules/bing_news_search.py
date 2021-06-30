from selenium import webdriver
from bs4 import BeautifulSoup
import re
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
from time import sleep
import datetime
import time
from config import Config
import redis
import multiprocessing
import json
import indicoio
from modules.caps_client import CapsClient
from modules import minio_push


class BingNewsSearch:

    def __init__(self):

        # self.proxy = self._get_proxy()

        indicoio.config.api_key = CapsClient().get_credential_random('indico', 'api_key')['api_key']['access_token']
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extension")
        options.add_argument("--proxy-server={}".format(self._get_proxy()))
        # options.add_argument("--proxy-server=socks5://176.107.177.59:3388")

        # local selenium webdriver
        # self.driver = webdriver.Chrome(options=options)
        #
        # remote webdriver
        self.driver = webdriver.Remote(
            command_executor=Config.SELENIUM_URI,
            desired_capabilities=options.to_capabilities(),
        )

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
        client_id = 'bing_news_service_' + selenium_session
        p = r.pubsub()  # pubsub object
        p.subscribe(client_id)
        return client_id, r, p

    def parser(self, htmldata, client_id, redis_obj, index_to_process):

        soup = BeautifulSoup(htmldata, features="lxml")
        post = soup.find('div', class_='algocore').find_all('div', class_='news-card newsitem cardcommon')
        start_from = index_to_process

        for listdata in post[start_from:]:
            temp_dict = dict()
            try:
                temp_dict['title'] = listdata.find('a', class_='title').text
            except:
                temp_dict['title'] = None
            try:
                data = listdata.find('div', class_='source').text
                source_data = listdata.find('div', class_='source').find('a').text
                final_date = data.split(source_data)[1]
                if 'h' in final_date:
                    post_time = datetime.datetime.now() - datetime.timedelta(hours=int(final_date.lstrip()[0:1]))
                    post_time = post_time.strftime('%Y-%m-%d %H:%M:%S')
                    final_date = time.mktime(datetime.datetime.strptime(post_time, "%Y-%m-%d %H:%M:%S").timetuple())
                elif 'd' in final_date:
                    post_time = datetime.datetime.now() - datetime.timedelta(days=int(final_date.lstrip()[0:1]))
                    post_time = post_time.strftime('%Y-%m-%d %H:%M:%S')
                    final_date = time.mktime(datetime.datetime.strptime(post_time, "%Y-%m-%d %H:%M:%S").timetuple())
                elif 'm' in final_date:
                    post_time = datetime.datetime.now() - datetime.timedelta(minutes=int(final_date.lstrip()[0:1]))
                    post_time = post_time.strftime('%Y-%m-%d %H:%M:%S')
                    final_date = time.mktime(datetime.datetime.strptime(post_time, "%Y-%m-%d %H:%M:%S").timetuple())
                temp_dict['datetime'] = int(final_date)
            except:
                temp_dict['datetime'] = None
            try:
                temp_dict['source'] = listdata.find('div', class_='source').find('a').text
                temp_dict['source_url'] = 'https://www.bing.com/' + listdata.find('div', class_='source').find('a').get(
                    'href')
            except:
                temp_dict['source'] = None
                temp_dict['source_url'] = None
            try:
                temp_dict['url'] = listdata.find('a').get('href')
            except:
                temp_dict['url'] = None
            try:
                temp_dict['content'] = listdata.find('div', class_='snippet').text
                temp_dict['polarity'] = self.indico_sentiment(temp_dict['content'])
            except:
                temp_dict['content'] = None
                temp_dict['polarity'] = None

            try:
                image_url = listdata.find('div', class_='image').find('img').get('src')
                if 'base64' in image_url:
                    pass
                else:
                    image_url = ('https://bing.com/' + image_url)

                minio_url = minio_push.start_uploading([image_url], 'bing-service')
                for i in minio_url:
                    if i['status'] == 200:
                        temp_dict['thumbnail'] = i['file_url']
                    else:
                        raise Exception('image not found')
            except:
                temp_dict['thumbnail'] = None

            temp_dict['type'] = 'news'

            print(temp_dict)

            index_to_process += 1
            redis_obj.publish(client_id, json.dumps(temp_dict))

        return index_to_process

    def pagination(self, client_id, redis_obj, channel_obj):
        print('scrolling starts')
        index_to_process = 0
        count = 0
        condition = True

        while condition:
            count += 1
            try:
                start_from = self.parser(self.driver.page_source, client_id, redis_obj, index_to_process)
                index_to_process = start_from

                if self.driver.execute_script(
                        "return document.getElementById('news').children[1].scrollHeight") - self.driver.execute_script(
                        "return document.getElementById('news').children[1].scrollTop") == self.driver.execute_script(
                    "return document.getElementById('news').children[1].clientHeight"):
                    print("you're at the bottom of the page")
                    condition = False

                else:
                    self.driver.execute_script("document.getElementById('news').children[1].scrollBy(0, 5000)")
                    condition = True
                time.sleep(1)

            except Exception as e:
                print(e)
                redis_obj.publish(client_id, 'EOF')
                channel_obj.unsubscribe(client_id)
                self.driver.quit()

            if count == 20:
                redis_obj.publish(client_id, 'EOF')
                channel_obj.unsubscribe(client_id)
                self.driver.quit()

    def get(self, query, time_duration=None):

        print("query: ", query)

        # self.driver.get(f"https://www.bing.com/search?q={query}&setmkt=en-us")
        self.driver.get(f"https://www.bing.com/news/search?q={query}&setmkt=en-us")

        sleep(1)
        try:
            self.driver.find_element_by_link_text('Date').click()
        except exceptions.NoSuchElementException:
            self.driver.find_element_by_link_text('Any time').click()
        sleep(1)
        if time_duration:

            if time_duration == 'past_hour':
                self.driver.find_element_by_link_text('Past hour').click()
            elif time_duration == 'past_day':
                self.driver.find_element_by_link_text('Past 24 hours').click()
            elif time_duration == 'past_week':
                self.driver.find_element_by_link_text('Past 7 days').click()
            elif time_duration == 'past_month':
                self.driver.find_element_by_link_text('Past 30 days').click()

        try:
            self.driver.find_element_by_xpath("//main[@class='main']")
        except exceptions.NoSuchElementException:
            self.driver.quit()
            return {"message": "no data found"}

        selenium_session_id = self.driver.session_id
        client_id, redis_obj, channel_obj = self.redis_channel(selenium_session_id)

        t = multiprocessing.Process(target=self.pagination, args=(client_id, redis_obj, channel_obj))
        t.start()

        return {"channel_id": client_id}

    def processor(self, q=None, site=None, time_duration=None, exclude=None):

        # query filters
        query = ''
        if q:
            query += f'{q}'
        if exclude:
            query += f' -{exclude}'
        if site:
            query += f' site:{site}'

        lis_res = self.get(query, time_duration)
        return lis_res


if __name__ == '__main__':
    Obj = BingNewsSearch()
    # print(Obj.processor(q='trump', exclude='donald', site='bbc.com', time_duration='past_month'))
    print(Obj.processor(q='trump', exclude='donald', time_duration='past_week'))

# time_duration='past_month'
