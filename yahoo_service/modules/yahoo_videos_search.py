from selenium import webdriver
from selenium.common import exceptions
from bs4 import BeautifulSoup
from modules.caps_client import CapsClient
from time import sleep
import datetime
from config import Config
from urllib.parse import quote
import time
import json
import redis
import multiprocessing
from modules import minio_push


class YahooVideoSearch:

    def __init__(self):

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

    def redis_channel(self, selenium_session):

        r = redis.from_url("redis://{}".format(Config.REDIS_URI))
        client_id = 'yahoo_videos_service_' + selenium_session
        p = r.pubsub()  # pubsub object
        p.subscribe(client_id)
        return client_id, r, p

    def parser(self, htmldata, client_id, redis_obj, index_to_process):
        soup = BeautifulSoup(htmldata, features='lxml')
        post = soup.find('div', id='main').find('div', class_='results clearfix').find_all('li')
        for listdata in post[index_to_process:]:
            if listdata.find('a') in listdata:
                index_to_process += 1
                temp_dict = dict()
                try:
                    temp_dict['title'] = listdata.find('h3').text
                except:
                    temp_dict['title'] = None
                try:
                    temp_dict['source'] = listdata.find('cite').text
                except:
                    temp_dict['source'] = None
                try:
                    temp_dict['url'] = listdata.find('a').get('data-rurl')
                except:
                    temp_dict['url'] = None
                try:
                    duration = listdata.find('span', class_='v-time').text
                    duration_data = duration.split(':')
                    if len(duration_data) == 2:
                        duration = (int(duration_data[0])*60)+(int(duration_data[1]))
                    elif len(duration_data) == 3:
                        duration = (int(duration_data[0])*1200)+(int(duration_data[1])*60)+(int(duration_data[2]))
                    else:
                        pass
                    temp_dict['video_length'] = duration
                except:
                    temp_dict['video_length'] = None
                try:
                    date_raw = listdata.find('div', class_='v-age').text
                    if 'hour' in date_raw:
                        final_data = datetime.datetime.now() - datetime.timedelta(hours=int(date_raw.lstrip()[0:2]))
                    elif 'minute' in date_raw:
                        final_data = datetime.datetime.now() - datetime.timedelta(minutes=int(date_raw.lstrip()[0:2]))
                    elif 'day' in date_raw:
                        final_data = datetime.datetime.now() - datetime.timedelta(days=int(date_raw.lstrip()[0:2]))
                    elif 'year' in date_raw:
                        final_data = datetime.datetime.now() - datetime.timedelta(days=int(date_raw.lstrip()[:2]) * 365)
                    elif 'month' in date_raw:
                        final_data = datetime.datetime.now() - datetime.timedelta(days=int(date_raw.lstrip()[:2]) * 365 / 12)

                    final_data = final_data.strftime('%Y-%m-%d %H:%M:%S')
                    temp_dict['datetime'] = int(time.mktime(datetime.datetime.strptime(
                        final_data, "%Y-%m-%d %H:%M:%S").timetuple()))
                except:
                    temp_dict['datetime'] = None
                try:
                    image_url = listdata.find('img').get('src')
                    minio_url = minio_push.start_uploading([image_url],'yahoo-service')
                    for i in minio_url:
                        if i['status'] == 200:
                            temp_dict['thumbnail'] = i['file_url']
                        else:
                            raise Exception('image not found')
                except:
                    temp_dict['thumbnail'] = None

                temp_dict['type'] = 'video'

                print(temp_dict)
                if temp_dict['title']:
                    redis_obj.publish(client_id, json.dumps(temp_dict))
            else:
                pass

        return index_to_process

    def pagination(self, client_id, redis_obj, channel_obj):
        count = 0
        index_to_process = 0
        while True:
            count += 1
            if count == 5:
                redis_obj.publish(client_id, 'EOF')
                channel_obj.unsubscribe(client_id)
                self.driver.quit()
                break
            try:
                time.sleep(1)
                start_from = self.parser(self.driver.page_source, client_id, redis_obj, index_to_process)
                index_to_process = start_from
                self.driver.execute_script('window.scrollBy(0, document.body.scrollHeight)')
                sleep(1)
                try:
                    self.driver.find_element_by_xpath('//button[text()="Show More Videos"]').click()
                except exceptions.NoSuchElementException:
                    redis_obj.publish(client_id, 'EOF')
                    channel_obj.unsubscribe(client_id)
                    self.driver.quit()
                    break

                sleep(1)
            except Exception as e:
                print(e)
                redis_obj.publish(client_id, 'EOF')
                channel_obj.unsubscribe(client_id)
                self.driver.quit()
                break

    def get(self, q, time_duration):

        url = f'https://search.yahoo.com/search?p={q}'
        self.driver.get(url)

        # when 'oath' is required to get the page
        try:
            self.driver.find_element_by_xpath("/html/body/div/div/div/form/div/button[@name='agree']").click()
        except exceptions.NoSuchElementException:
            pass

        self.driver.find_element_by_link_text('Video').click()
        sleep(1)

        # date_ formatting
        if time_duration:
            self.driver.find_element_by_xpath("//div[@id='horiz-filters']/ul/li[2]/span/span").click()
            sleep(2)
            try:

                if time_duration == 'past_day':
                    self.driver.find_element_by_link_text('Past 24 hours').click()
                elif time_duration == 'past_week':
                    self.driver.find_element_by_link_text('Past week').click()
                elif time_duration == 'past_month':
                    self.driver.find_element_by_link_text('Past month').click()
                if time_duration == 'past_year':
                    self.driver.find_element_by_link_text('Past year').click()
            except exceptions.NoSuchElementException:
                print('date filter not clickable')

        # check for search results
        try:
            self.driver.find_element_by_xpath("//section[@id='search']")

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

    def processor(self, q=None, exclude=None, site=None, time_duration=None):

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

        lis_res = self.get(q, time_duration)
        return lis_res


if __name__ == '__main__':
    Obj = YahooVideoSearch()
    print(Obj.processor(q='trump', exclude='donald', site='bbc.com', time_duration='past_year'))
    # print(Obj.processor(q='trump', site='bbc.com'))


