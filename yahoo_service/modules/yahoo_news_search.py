from selenium import webdriver
from selenium.common import exceptions
from bs4 import BeautifulSoup
from modules.caps_client import CapsClient
from time import sleep
from config import Config
import datetime
import multiprocessing
from urllib.parse import quote, unquote
import redis
import json
import time
from modules import minio_push
import indicoio


class YahooNewsSearch:

    def __init__(self):

        indicoio.config.api_key = CapsClient().get_credential_random('indico', 'api_key')['api_key']['access_token']
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extension")
        options.add_argument("--proxy-server={}".format(self._get_proxy()))

        # local selenium webdriver
        # self.driver = webdriver.Chrome(options=options)

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

    # sentiment analysis
    def indico_sentiment(self, data):

        pol = indicoio.sentiment(data)
        if pol > 0.7000000000000000:
            return "positive"
        elif pol < 0.3000000000000000:
            return "negative"
        else:
            return "neutral"

    def redis_channel(self, selenium_session):

        r = redis.from_url("redis://{}".format(Config.REDIS_URI))
        client_id = 'yahoo_news_service_' + selenium_session
        p = r.pubsub()  # pubsub object
        p.subscribe(client_id)
        return client_id, r, p

    def parser(self, htmldata, client_id, redis_obj):

        soup = BeautifulSoup(htmldata, features='lxml')
        for listdata in soup.find('div', id='main').find('ol'):
            temp_dict = dict()
            try:
                temp_dict['title'] = listdata.find('h4').text
            except:
                temp_dict['title'] = None
            try:
                temp_url = listdata.find('a').get('href')
                temp_dict['url'] = unquote(temp_url[temp_url.index('RO=10/RU=')+9:temp_url.index('/RK=2/RS=')])
            except:
                temp_dict['url'] = None
            try:
                date_raw = listdata.find('span', class_='fc-2nd mr-8').text
                date_raw = date_raw.split('·')[1]
                if 'hour' in date_raw:
                    final_data = datetime.datetime.now() - datetime.timedelta(hours=int(date_raw.lstrip()[0:2]))
                elif 'minute' in date_raw:
                    final_data = datetime.datetime.now() - datetime.timedelta(minutes=int(date_raw.lstrip()[0:2]))
                elif 'day' in date_raw:
                    final_data = datetime.datetime.now() - datetime.timedelta(days=int(date_raw.lstrip()[0:2]))
                elif 'year' in date_raw:
                    final_data = datetime.datetime.now() - datetime.timedelta(days=int(date_raw.lstrip()[:2]) * 365)
                elif 'month' in date_raw:
                    final_data = datetime.datetime.now() - datetime.timedelta(
                        days=int(date_raw.lstrip()[:2]) * 365 / 12)

                final_data = final_data.strftime('%Y-%m-%d %H:%M:%S')
                final_data = time.mktime(datetime.datetime.strptime(final_data, "%Y-%m-%d %H:%M:%S").timetuple())
                temp_dict['datetime'] = int(final_data)
            except:
                temp_dict['datetime'] = None
            try:
                temp_dict['source'] = listdata.find('span').text
            except:
                temp_dict['source'] = None
            try:
                temp_dict['content'] = listdata.find('p').text
                temp_dict['polarity'] = self.indico_sentiment(temp_dict['content'])
            except:
                temp_dict['content'] = None
                temp_dict['polarity'] = 'neutral'

            try:
                image_url = listdata.find('img').get('src')
                minio_url = minio_push.start_uploading([image_url], 'yahoo-service')
                for i in minio_url:
                    if i['status'] == 200:
                        temp_dict['thumbnail'] = i['file_url']
                    else:
                        raise Exception('image not found')
            except:
                temp_dict['thumbnail'] = None

            temp_dict['type'] = 'news'

            if temp_dict['title']:
                redis_obj.publish(client_id, json.dumps(temp_dict))
            print(temp_dict)
        return True

    def pagination(self, client_id, redis_obj, channel_obj):
        count = 1
        while True:
            count += 1
            if count == 20:
                redis_obj.publish(client_id, 'EOF')
                channel_obj.unsubscribe(client_id)
                self.driver.quit()

            try:
                htmldata = self.driver.page_source
                self.parser(htmldata, client_id, redis_obj)
                sleep(0.5)
                self.driver.find_element_by_link_text('Next').click()
                sleep(1)
            except Exception as e:
                # print(e)
                redis_obj.publish(client_id, 'EOF')
                channel_obj.unsubscribe(client_id)
                self.driver.quit()

    def get(self, q):

        url = f'https://search.yahoo.com/search?p={q}'
        self.driver.get(url)

        # when 'oath' is required to get the page
        try:
            self.driver.find_element_by_xpath("/html/body/div/div/div/form/div/button[@name='agree']").click()
        except exceptions.NoSuchElementException:
            pass
        sleep(1)

        self.driver.find_element_by_link_text('News').click()

        # check for search results
        try:
            self.driver.find_element_by_xpath("//div[@id='main']/div/div[@id='web']/ol/li[@class='first']")

        except exceptions.NoSuchElementException:
            self.driver.quit()
            return {"message": "no data found"}

        selenium_session_id = self.driver.session_id
        client_id, redis_obj, channel_obj = self.redis_channel(selenium_session_id)
        #
        t = multiprocessing.Process(target=self.pagination, args=(client_id, redis_obj, channel_obj))
        t.start()
        #
        return {"channel_id": client_id}

    def processor(self, q=None, exclude=None, site=None):

        query_string = ''
        if exclude and site:
            query_string = f'"{q}" -{exclude} site:{site}'

        elif exclude:
            query_string = f'"{q}" -{exclude}'

        elif site:
            query_string = f'"{q}" site:{site}'

        else:
            query_string = f'"{q}"'

        print({"query": query_string})

        q = quote(query_string)

        lis_res = self.get(q)
        return lis_res

# ------------------------------------------------------


if __name__ == '__main__':
    Obj = YahooNewsSearch()
    # print(Obj.processor(q='trump', exclude='donald', site='forbes.com'))
    print(Obj.processor(q='trump', site='bbc.com'))

