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


class BingVideosSearch:

    def __init__(self):

        # self.proxy = self._get_proxy()

        indicoio.config.api_key = CapsClient().get_credential_random('indico', 'api_key')['api_key']['access_token']
        # indicoio.config.api_key = 'a40c4ac2fdc7bcbd071772813b75244c'
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
        client_id = 'bing_videos_service_' + selenium_session
        p = r.pubsub()  # pubsub object
        p.subscribe(client_id)
        return client_id, r, p

    def parser(self, htmldata, client_id, redis_obj, index_to_process):

        soup = BeautifulSoup(htmldata, features="lxml")
        for listdata in soup.find('div', class_='dg_b'):
            # print(listdata)
            index_to_process += 1
            temp_dict = dict()
            try:
                temp_dict['title'] = listdata.find('strong').text
            except:
                temp_dict['title'] = None
            try:
                data = listdata.find('div', class_='mc_vtvc_meta_row').text
                if 'views' in data:
                    data = data.split('views')
                    time_data = data[1]
                else:
                    time_data = data
                final_data = ''
                if 'year' in time_data:
                    final_data = datetime.datetime.now() - datetime.timedelta(days=int(time_data.lstrip()[:2]) * 365)
                elif 'month' in time_data:
                    final_data = datetime.datetime.now() - datetime.timedelta(
                        days=int(time_data.lstrip()[:2]) * 365 / 12)
                elif 'week' in time_data:
                    final_data = datetime.datetime.now() - datetime.timedelta(days=int(time_data.lstrip()[:2]) * 7)
                elif 'hour' in time_data:
                    final_data = datetime.datetime.now() - datetime.timedelta(hours=int(time_data.lstrip()[0:2]))
                elif 'minute' in time_data:
                    final_data = datetime.datetime.now() - datetime.timedelta(minutes=int(time_data.lstrip()[0:2]))
                elif 'day' in time_data:
                    final_data = datetime.datetime.now() - datetime.timedelta(days=int(time_data.lstrip()[0:2]))

                final_data = final_data.strftime('%Y-%m-%d %H:%M:%S')
                final_data = time.mktime(datetime.datetime.strptime(final_data, "%Y-%m-%d %H:%M:%S").timetuple())
                temp_dict['datetime'] = int(final_data)

            except:
                temp_dict['datetime'] = None
            try:
                data = listdata.find('div', class_='mc_vtvc_meta_row').text
                views = data.split('views')[0]
                if 'K' in views:
                    views = float(views.replace('K', ''))
                    views = int(views * 1000)
                elif 'M' in views:
                    views = float(views.replace(',', '').replace('M', ''))
                    views = int(views * 1000000)
                temp_dict['views'] = int(views)
            except:
                temp_dict['views'] = None
            try:
                temp_dict['url'] = 'https://www.bing.com' + listdata.find('a').get('href')
            except:
                temp_dict['url'] = None
            try:
                duration = listdata.find('div', class_='mc_bc_rc items').text
                duration_data = duration.split(':')
                if len(duration_data) == 2:
                    duration = (int(duration_data[0]) * 60) + (int(duration_data[1]))
                elif len(duration_data) == 3:
                    duration = (int(duration_data[0]) * 1200) + (int(duration_data[1]) * 60) + (int(duration_data[2]))
                else:
                    pass
                temp_dict['video_length'] = duration
            except:
                temp_dict['video_length'] = None
            try:
                temp_dict['source'] = listdata.find_all('div', class_='mc_vtvc_meta_row')[1].find('span').text
            except:
                temp_dict['source'] = None
            try:
                temp_dict['source_channel'] = listdata.find('span', class_='mc_vtvc_meta_row_channel').text
            except:
                temp_dict['source_channel'] = None
            try:
                sleep(0.5)
                image_url = listdata.find('img').get('src')
                if 'base64' in image_url:
                    pass
                else:
                    image_url = ('https://www.bing.com' + image_url)

                minio_url = minio_push.start_uploading([image_url], 'bing-service')
                for i in minio_url:
                    if i['status'] == 200:
                        temp_dict['thumbnail'] = i['file_url']
                    else:
                        raise Exception('image not found')
            except:
                temp_dict['thumbnail'] = None
            try:
                temp_dict['type'] = 'video'
            except:
                temp_dict['type'] = None

            if temp_dict['title']:
                redis_obj.publish(client_id, json.dumps(temp_dict))
                print(temp_dict)
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

                if self.driver.execute_script("return window.innerHeight") + self.driver.execute_script(
                        "return window.scrollY") >= self.driver.execute_script("return document.body.offsetHeight"):
                    print("you're at the bottom of the page")
                    condition = False
                else:
                    self.driver.execute_script("window.scrollBy(0, 1000);")
                    time.sleep(2)

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
        base_url = f'https://www.bing.com/videos/search?q={query}&setmkt=en-us'

        if time_duration:

            if time_duration == 'past_day':
                self.driver.get(f"{base_url}&qft=+filterui:videoage-lt1440&FORM=VRFLTR")
            elif time_duration == 'past_week':
                self.driver.get(f"{base_url}&qft=+filterui:videoage-lt10080&FORM=VRFLTR")
            elif time_duration == 'past_month':
                self.driver.get(f"{base_url}&qft=+filterui:videoage-lt43200&FORM=VRFLTR")
            elif time_duration == 'past_year':
                self.driver.get(f"{base_url}&qft=+filterui:videoage-lt525600&FORM=VRFLTR")
        else:
            self.driver.get(base_url)

        sleep(1)
        try:
            self.driver.find_element_by_xpath("//div[@id='vm_c']/div[@id='dg_c']")
        except exceptions.NoSuchElementException:
            self.driver.quit()
            return {"message": "no data found"}
        sleep(2)
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
    Obj = BingVideosSearch()
    # print(Obj.processor(q='trump', exclude='donald', site='bbc.com', time_duration='past_month'))
    print(Obj.processor(q='trump', exclude='donald', time_duration='past_month'))

# time_duration='past_month'
