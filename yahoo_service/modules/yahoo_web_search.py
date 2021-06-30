from selenium import webdriver
from selenium.common import exceptions
from modules.caps_client import CapsClient
from bs4 import BeautifulSoup
from time import sleep
from config import Config
import redis
import time
import re
import json
import multiprocessing
import indicoio
from urllib.parse import quote


class YahooSearch:

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

        # r = redis.Redis(host=self.redis_host, port=self.redis_port)
        r = redis.from_url("redis://{}".format(Config.REDIS_URI))
        client_id = 'yahoo_web_service_' + selenium_session
        p = r.pubsub()  # pubsub object
        p.subscribe(client_id)
        return client_id, r, p

    def parser(self, htmldata, client_id, redis_obj):

        soup = BeautifulSoup(htmldata, features="lxml")
        for listdata in soup.find('div', id='main').find('ol').find_all(class_=re.compile("dd algo algo-sr")):
            # print(listdata)

            temp_dict = dict()
            try:
                temp_dict['title'] = listdata.find('h3').text
            except:
                temp_dict['title'] = None
            try:
                temp_dict['url'] = listdata.find('a').get('href')
            except:
                temp_dict['url'] = None
            try:
                temp_dict['content'] = listdata.find('p').text
                temp_dict['polarity'] = self.indico_sentiment(temp_dict['content'])
            except:
                temp_dict['content'] = None
                temp_dict['polarity'] = 'neutral'

            temp_dict['type'] = 'link'

            print(temp_dict)

            if temp_dict['title']:
                redis_obj.publish(client_id, json.dumps(temp_dict))

        return

    def pagination(self, client_id, redis_obj, channel_obj):
        count = 0
        while True:
            count += 1
            if count == 4:
                redis_obj.publish(client_id, 'EOF')
                channel_obj.unsubscribe(client_id)
                self.driver.quit()
                break
            try:
                htmldata = self.driver.page_source
                self.parser(htmldata, client_id, redis_obj)
                print('click next')
                sleep(2)

                self.driver.execute_script('window.scrollBy(0, document.body.scrollHeight)')
                self.driver.find_element_by_class_name('next').click()
                print('clicked')
                sleep(1)
            except Exception as e:
                # print(e)
                redis_obj.publish(client_id, 'EOF')
                channel_obj.unsubscribe(client_id)
                self.driver.quit()
                break
            time.sleep(1)

    def get(self, url_to_process):

        print("url:", url_to_process)

        self.driver.get(url_to_process)

        # when 'oath' is required to get the page
        try:
            self.driver.find_element_by_xpath("/html/body/div/div/div/form/div/button[@name='agree']").click()
        except exceptions.NoSuchElementException:
            pass
        sleep(1)

        # check for search results
        try:
            first_element = self.driver.find_element_by_xpath("//div[@id='web']/ol/li[@class='first']")

            '''find elements with CSS Selectors, partial match on attribute values'''
            first_element.find_element_by_css_selector("div[class^='dd algo algo-sr']")

        except exceptions.NoSuchElementException:
            self.driver.quit()
            return {"message": "no data found"}

        selenium_session_id = self.driver.session_id
        client_id, redis_obj, channel_obj = self.redis_channel(selenium_session_id)
        #
        t = multiprocessing.Process(target=self.pagination, args=(client_id, redis_obj, channel_obj))
        t.start()

        return {"channel_id": client_id}

    def processor(self, q=None, exclude=None, site=None, filetype=None, time_duration=None):

        # date_ formatting
        if time_duration == 'past_day':
            time_duration = 'd'
        elif time_duration == 'past_week':
            time_duration = 'w'
        elif time_duration == 'past_month':
            time_duration = 'm'

        url = 'https://search.yahoo.com/search?n=100'

        if filetype:
            url += f'&vf={filetype}'
        if q:
            q = quote(q)
            url += f'&p="{q}"'
        if exclude:
            url += f'+-{exclude}'
        if site:
            url += f'&vs={site}'
        if time_duration:
            url += f'&btf={time_duration}'

        # ----------------------------------------------------------

        lis_res = self.get(url)
        return lis_res


if __name__ == '__main__':
    Obj = YahooSearch()
    print(Obj.processor(q='mila kunis', site='forbes.com'))
    # print(Obj.processor(q='mila kunis'))
