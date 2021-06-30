import json
from urllib.parse import unquote
from time import sleep
import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException
import urllib.parse
from credential import creds
import re
import datetime
import demjson
from config import Config
import redis
import asyncio
import threading, multiprocessing


class PostSearch2:

    def __init__(self):

        self.redis_host = Config.REDIS_CONFIG['host']
        self.redis_port = Config.REDIS_CONFIG['port']
        self.Cookies = json.loads(creds['cookies'])
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extension")
        prefs = {"profile.default_content_setting_values.notifications": 2}
        options.add_experimental_option("prefs", prefs)

        # options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)

        # remote webdriver
        # self.driver = webdriver.Remote(
        #     command_executor='http://' + Config.SELENIUM_CONFIG['host'] + ':' + Config.SELENIUM_CONFIG[
        #         'port'] + '/wd/hub',
        #     desired_capabilities=options.to_capabilities(),
        # )

        url = "http://www.facebook.com"

        self.driver.get(url)

        for cookie in self.Cookies:
            self.driver.add_cookie(cookie)


    def redis_channel(self, selenium_session):
        r = redis.Redis(host=self.redis_host, port=self.redis_port)
        client_id = 'facebook_service_' + selenium_session
        p = r.pubsub()  #pubsub object
        p.subscribe(client_id)
        return client_id, r, p


    def fb_posts(self, query):

        query = urllib.parse.quote(query)
        # self.driver.get('https://www.facebook.com/search/posts/?q={}&epa=SERP_TAB'.format(query))
        self.driver.get('https://www.facebook.com/search/str/{}/stories-keyword'.format(query))
        sleep(0.2)

        try:
            self.driver.find_element_by_id('empty_result_error')
            self.driver.close()
            self.driver.quit()
            return 'no results found'
        except:

            selenium_session_id = self.driver.session_id
            client_id, redis_obj, channel_obj = self.redis_channel(selenium_session_id)

            # t = threading.Thread(target=self.get_posts, args=(self.driver, client_id, redis_obj, channel_obj))
            t = multiprocessing.Process(target=self.get_posts, args=(self.driver, client_id, redis_obj, channel_obj))
            t.start()

            return client_id

    def post_process(self, driver, index_to_process, redis_obj, client_id, channel_obj):
        try:
            posts = driver.find_elements_by_class_name('_5bl2')
            start_from = index_to_process

            for i in posts[start_from:]:
                start_from += 1

                rank_data = i.get_attribute('data-bt')
                rank_data_json = json.loads(rank_data)
                # print('#####')
                # print(rank_data_json)
                # print('####')
                if rank_data_json['rank'] > 100:
                    return 'results_threshold_reached'


                else:

                    temp_dict = {}
                    try:
                        temp_dict['author_image'] = i.find_element_by_class_name('_s0').get_attribute('src')
                    except:
                        temp_dict['author_image'] = None

                    try:
                        name_span = i.find_element_by_class_name('fwb')
                        temp_dict['author_name'] = name_span.find_element_by_tag_name('a').text
                        temp_dict['author_id'] = name_span.find_element_by_tag_name('a').get_attribute('href').split('/?')[0].replace('https://www.facebook.com/', '')
                    except:
                        temp_dict['author_name'] = None
                        temp_dict['author_id'] = None

                    try:
                        i.find_element_by_class_name('_56_f')
                        temp_dict['verified'] = True
                    except:
                        temp_dict['verified'] = False

                    try:
                        temp_dict['datetime'] = i.find_element_by_class_name('_5ptz').get_attribute('data-utime')
                    except:
                        temp_dict['datetime'] = None

                    try:
                        try:
                            temp_dict['thumbnail'] = i.find_element_by_class_name('scaledImageFitWidth').get_attribute('src')
                        except:
                            temp_dict['thumbnail'] = i.find_element_by_class_name('scaledImageFitHeight').get_attribute('src')
                    except:
                        temp_dict['thumbnail'] = None

                    try:
                        temp_dict['content_link'] = i.find_element_by_class_name('_52c6').get_attribute('href')
                    except:
                        temp_dict['content_link'] = None

                    try:
                        temp_dict['header'] = i.find_element_by_class_name('userContent').text
                    except:
                        temp_dict['header'] = None

                    try:
                        temp_dict['video_url'] = i.find_element_by_class_name('_5p5v').get_attribute('href')
                        temp_dict['video_thumbnail'] = i.find_element_by_class_name('_3chq').get_attribute('src')
                    except:
                        temp_dict['video_url'] = None
                        temp_dict['video_thumbnail'] = None

                    try:
                        gif_element = i.find_element_by_class_name('_6o4')
                        temp_dict['is_gif'] = True
                        temp_dict['gif_link'] = gif_element.find_elements_by_tag_name('span')[1].get_attribute('href')
                    except:
                        temp_dict['is_gif'] = True
                        temp_dict['gif_link'] = None


                    try:
                        temp_dict['likes'] = i.find_element_by_class_name('_3dlh').text

                    except:
                        temp_dict['likes'] = None

                    try:
                        album_element = i.find_element_by_class_name('_2a2q')
                        temp_dict['post_album'] = True
                        all_album_posts = album_element.find_elements_by_tag_name('a')
                        total_links = []
                        for single_album_post in all_album_posts:
                            link = single_album_post.find_element_by_tag_name('img').get_attribute('src')
                            total_links.append(link)
                        temp_dict['post_album_links'] = total_links
                    except:
                        temp_dict['post_album'] = False
                        temp_dict['post_album_links'] = None

                    try:
                        temp_dict['comments'] = i.find_element_by_class_name('_3hg-').text
                    except:
                        temp_dict['comments'] = None

                    try:
                        temp_dict['shares'] = i.find_element_by_class_name('_355t').text
                    except:
                        temp_dict['shares'] = None

                # str(temp_dict)
                # print(client_id)
                    print(temp_dict)
                    redis_obj.publish(client_id, json.dumps(temp_dict))

            loading = self.process_loading(driver)
            if loading:
                return start_from
            else:
                raise Exception('error in loading')

        except Exception as e:
            print('######')
            print(e)
            return 'ERROR'

    def get_posts(self, driver, client_id, redis_obj, channel_obj, index_to_process=0):
        process = self.post_process(driver, index_to_process, redis_obj, client_id, channel_obj)
        if process == 'results_threshold_reached' or process == 'ERROR':
            redis_obj.publish(client_id, 'EOF')
            channel_obj.unsubscribe(client_id)
            driver.close()
            driver.quit()
            return

        else:
            self.get_posts(driver, client_id, redis_obj, channel_obj, index_to_process=process)

        return

    def check_loading(self, driver):
        try:
            loading = driver.find_element_by_class_name('_akp')
            # loading.find_e
            WebDriverWait(loading, 15).until(ec.presence_of_all_elements_located((By.CLASS_NAME, 'hidden_elem')))
            return False
        except:
            return True

    def process_loading(self, driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        loading_in_progress = self.check_loading(driver)
        print(loading_in_progress)
        while loading_in_progress:
            time.sleep(2)
        return True


if __name__ == '__main__':
    obj = PostSearch2()
    print(obj.fb_posts('Nguyễn Phú Trọng'))
