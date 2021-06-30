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


class BingSearch:

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
        client_id = 'bing_web_service_' + selenium_session
        p = r.pubsub()  # pubsub object
        p.subscribe(client_id)
        return client_id, r, p

    def parser(self, html_data, client_id, redis_obj):

        soup = BeautifulSoup(html_data, 'lxml').find('ol', id='b_results')
        # print(soup.prettify())

        for each_search in soup.find_all('li', class_='b_algo'):
            # print(each_search)

            temp_dict = dict()

            temp_dict['title'] = each_search.find('h2').text

            temp_dict['url'] = each_search.find('h2').find('a').get('href')
            # print('p starts')
            try:
                data = each_search.find('p').text
                # print('p done')
                if '·' in data:
                    raw_data = data.split('·')[1]
                    temp_dict['content'] = raw_data
                else:
                    temp_dict['content'] = data
                temp_dict['polarity'] = self.indico_sentiment(temp_dict['content'])
            except Exception as e:
                # print(e)
                temp_dict['content'] = None
                temp_dict['polarity'] = 'neutral'
            # print('came out of p')

            try:
                date_raw = each_search.find('p').find('span', class_='news_dt').text
                # print(date_raw)

                # DD.MM.YYYY format
                if re.compile(r"\d{2}\.\d{2}.\d{4}").match(date_raw):
                    temp_dict['datetime'] = int(time.mktime(time.strptime(date_raw, '%d.%m.%Y'))) - time.timezone

                # DD/MM/YYYY format
                elif re.compile(r"\d{2}/\d{2}/\d{4}").match(date_raw):
                    temp_dict['datetime'] = int(time.mktime(time.strptime(date_raw, '%d/%m/%Y'))) - time.timezone

                elif 'ago' in date_raw:
                    final_data = ''
                    if 'minute' in date_raw:
                        final_data = datetime.datetime.now() - datetime.timedelta(minutes=int(date_raw[0:2].rstrip()))
                    elif 'hour' in date_raw:
                        final_data = datetime.datetime.now() - datetime.timedelta(hours=int(date_raw[0:2].rstrip()))
                    elif 'day' in date_raw:
                        final_data = datetime.datetime.now() - datetime.timedelta(days=int(date_raw[0:2].rstrip()))
                    elif 'week' in date_raw:
                        final_data = datetime.datetime.now() - datetime.timedelta(weeks=int(date_raw[0:2].rstrip()))
                    elif 'month' in date_raw:
                        final_data = datetime.datetime.now() - datetime.timedelta(days=int(date_raw[0:2].rstrip())*30)
                    elif 'year' in date_raw:
                        final_data = datetime.datetime.now() - datetime.timedelta(days=int(date_raw[0:2].rstrip())*365)

                    final_data = final_data.strftime('%Y-%m-%d %H:%M:%S')
                    temp_dict['datetime'] = int(time.mktime(datetime.datetime.strptime(final_data, "%Y-%m-%d %H:%M:%S").timetuple()))
                # else:
                #     date_raw = date_raw.replace(',', '')
                #     temp_dict['datetime'] = int(time.mktime(datetime.datetime.strptime(date_raw, "%b %d %Y").timetuple()))
            except:
                temp_dict['datetime'] = None
            # print(temp_dict)
            # print('done with date selection')
            temp_dict['type'] = 'link'

            print(temp_dict)
            redis_obj.publish(client_id, json.dumps(temp_dict))

        return

    def pagination(self, client_id, redis_obj, channel_obj):
        # print('pagination starts')
        count = 0
        condition = True
        while condition:
            # print('in loop')
            try:
                count += 1
                html_data = self.driver.page_source
                self.parser(html_data, client_id, redis_obj)

                sleep(1)
                self.driver.find_element_by_xpath("//a[@title='Next page']").click()

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

        print("query:", query)

        # self.driver.get("http://www.bing.com/")
        # sleep(1)
        # search_box = self.driver.find_element_by_id('sb_form_q')
        # search_box.send_keys(query)
        # search_box.send_keys(Keys.ENTER)
        self.driver.get(f"https://www.bing.com/search?q={query}&setmkt=en-us")
        # driver.get(url + '&setmkt=en-us')
        sleep(1)
        try:
            self.driver.find_element_by_xpath("//*[@id='b_results']/li[@class='b_algo']")
        except exceptions.NoSuchElementException:
            self.driver.quit()
            return {"message": "no data found"}

        if time_duration or from_date or to_date:
            sleep(3)
            try:
                # self.driver.find_element_by_xpath("//div[@id='b_content']/main/*[@id='b_tween']/span[2]/a").click()
                try:
                    self.driver.find_element_by_link_text('Date').click()
                except exceptions.NoSuchElementException:
                    self.driver.find_element_by_link_text('Any time').click()
                sleep(1)

                # try:
                #     self.driver.find_element_by_link_text('Date').click()
                # except:
                #     self.driver.find_element_by_link_text('Any time').click()
                #     sleep(2)
                #
                if time_duration:

                    if time_duration == 'past_day':
                        self.driver.find_element_by_link_text('Past 24 hours').click()
                    elif time_duration == 'past_week':
                        self.driver.find_element_by_link_text('Past week').click()
                    elif time_duration == 'past_month':
                        self.driver.find_element_by_link_text('Past month').click()
                    elif time_duration == 'past_year':
                        self.driver.find_element_by_link_text('Past year').click()

                elif from_date and to_date:

                    time.sleep(1)
                    from_date = datetime.datetime.fromtimestamp(from_date).strftime('%d-%m-%Y')
                    self.driver.find_element_by_id('date_range_start').click()
                    self.driver.find_element_by_id('date_range_start').clear()
                    self.driver.find_element_by_id('date_range_start').click()
                    self.driver.find_element_by_id('date_range_start').send_keys(from_date)

                    to_date = datetime.datetime.fromtimestamp(to_date).strftime('%d-%m-%Y')
                    self.driver.find_element_by_id('date_range_end').click()
                    self.driver.find_element_by_id('date_range_end').clear()
                    self.driver.find_element_by_id('date_range_end').click()
                    self.driver.find_element_by_id('date_range_end').send_keys(to_date)
                    self.driver.find_element_by_id('time_filter_done_link').click()

                elif from_date:
                    time.sleep(1)

                    from_date = datetime.datetime.fromtimestamp(from_date).strftime('%d-%m-%Y')
                    self.driver.find_element_by_id('date_range_start').click()
                    self.driver.find_element_by_id('date_range_start').clear()
                    self.driver.find_element_by_id('date_range_start').click()
                    self.driver.find_element_by_id('date_range_start').send_keys(from_date)
                    self.driver.find_element_by_id('date_range_start').send_keys(Keys.ENTER)

                elif to_date:
                    to_date = datetime.datetime.fromtimestamp(to_date).strftime('%d-%m-%Y')
                    self.driver.find_element_by_id('date_range_start').click()
                    self.driver.find_element_by_id('date_range_start').clear()
                    self.driver.find_element_by_id('date_range_start').click()
                    self.driver.find_element_by_id('date_range_end').click()
                    self.driver.find_element_by_id('date_range_end').clear()
                    self.driver.find_element_by_id('date_range_end').click()
                    self.driver.find_element_by_id('date_range_end').send_keys(to_date)
                    sleep(0.5)

                    self.driver.find_element_by_id('date_range_end').send_keys(Keys.ENTER)

                # self.driver.find_element_by_link_text('Apply').click()
                # self.driver.find_element_by_xpath("//div[@class='modernCalIconContainer']/img").click()
                # sleep(2)
                # self.driver.find_element_by_id('time_filter_done_link').click()

            except exceptions.NoSuchElementException:
                print('date bar didn\'t appear')

        selenium_session_id = self.driver.session_id
        client_id, redis_obj, channel_obj = self.redis_channel(selenium_session_id)

        t = multiprocessing.Process(target=self.pagination, args=(client_id, redis_obj, channel_obj))
        t.start()

        return {"channel_id": client_id}

    def processor(self, q=None, filetype=None, site=None, time_duration=None, exclude=None, from_date=None, to_date=None):

        # query filters
        query = ''
        if q:
            query += f'{q}'
        if exclude:
            query += f' -{exclude}'
        if site:
            query += f' site:{site}'
        if filetype:
            query += f' filetype:{filetype}'

        lis_res = self.get(query, time_duration, from_date, to_date)
        return lis_res


if __name__ == '__main__':
    Obj = BingSearch()
    # print(Obj.processor(q='trump', exclude='donald', filetype='pdf', from_date=1445421244))
    print(Obj.processor(q='trump', filetype='pdf', to_date=1545421244))

# from_date=1445421244, to_date=1545421244
# time_duration='past_month'
