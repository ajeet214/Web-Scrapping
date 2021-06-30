import json
import redis
import time
import re
from selenium import webdriver
from urllib.parse import quote
from bs4 import BeautifulSoup
import multiprocessing
from config import Config
import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, UnableToSetCookieException
from selenium.webdriver.common.keys import Keys
from modules.caps_client import CapsClient, CredentialPlatform, CredentialType
import indicoio
from modules import minio_push


class SearchClass:

    def __init__(self):

        self.c = 0
        credential = CapsClient().get_credential_random(CredentialPlatform.LINKEDIN, CredentialType.COOKIES)

        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        # options.add_argument("--headless")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36")

        if credential['proxy']:
            options.add_argument(f"--proxy-server=socks5://{credential['proxy']['host']}:{credential['proxy']['port']}")
        else:
            pass

        # local webdriver
        # self.driver = webdriver.Chrome(options=options)

        # remote webdriver
        self.driver = webdriver.Remote(
            command_executor=Config.SELENIUM_URI,
            desired_capabilities=options.to_capabilities(),
        )

        url = "https://www.linkedin.com"

        self.driver.get(url)
        try:
            for cookie in credential['cookies']:
                self.driver.add_cookie(cookie)
        except UnableToSetCookieException as e:
            raise e.msg

    # -----------------------------------------------------------------------------

    def redis_channel(self, selenium_session):
        # r = redis.Redis(host=self.redis_host, port=self.redis_port)
        r = redis.from_url("redis://{}".format(Config.REDIS_URI))
        client_id = 'linkedin_post_service_' + selenium_session
        p = r.pubsub()  #pubsub object
        p.subscribe(client_id)
        return client_id, r, p

    def process_loading(self):

        if self.driver.execute_script("return window.innerHeight")+self.driver.execute_script(
                "return window.scrollY") >= self.driver.execute_script("return document.body.offsetHeight"):
            print("you're at the bottom of the page")
            return False
        else:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            return True

    def parser(self, start_from, redis_obj, client_id, channel_obj):

        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        # print(soup.prettify())
        # exit()
        posts = soup.find('ul', class_='search-results__list').find_all('li', class_="search-content__result")
        for each_element in posts[start_from:]:

            temp_dict = dict()
            temp_dict['url'] = f'https://www.linkedin.com/feed/update/{each_element.find(attrs={"class": re.compile(r"^feed-shared-update-v2 relative full-height")})["data-id"]}'

            actor = each_element.find('a', {"data-control-name": "actor_container"})
            # temp_dict['author_image'] = actor.img['src']
            temp_dict['author_url'] = actor['href']
            try:
                image_url = actor.find('img')['src']
                minio_url = minio_push.start_uploading([image_url], 'linkedin-service')
                for i in minio_url:
                    if i['status'] == 200:
                        temp_dict['author_image'] = i['file_url']
                    else:
                        raise Exception('image not found')

            except (KeyError, TypeError):
                temp_dict['author_image'] = None
            temp_dict['author_name'] = actor.h3.find('span', {"dir": "ltr"}).text
            # temp_dict['author_name'] = actor.img['alt']
            temp_dict['author_status'] = actor.find('span', class_='feed-shared-actor__description').text
            temp_dict['datetime'] = actor.find('span', class_='feed-shared-actor__sub-description').text.replace('\n',
                                                                                                                 ' ').replace(
                '• Edited', '').replace('Published •', '').strip()

            if temp_dict['datetime'].endswith('m'):
                post_time = datetime.datetime.now() - datetime.timedelta(
                    minutes=int(temp_dict['datetime'].replace('m', '')))
                post_time = post_time.strftime('%Y-%m-%d %H:%M:%S')

                # Convert from human readable date to epoch
                temp_dict['datetime'] = int(
                    time.mktime(time.strptime(post_time, '%Y-%m-%d %H:%M:%S'))) - time.timezone

            elif temp_dict['datetime'].endswith('h'):
                post_time = datetime.datetime.now() - datetime.timedelta(hours=int(
                    temp_dict['datetime'].replace('h', '')))
                post_time = post_time.strftime('%Y-%m-%d %H:%M:%S')

                # Convert from human readable date to epoch
                # int(time.mktime(time.strptime('2000-01-01 12:34:00', '%Y-%m-%d %H:%M:%S'))) - time.timezone
                temp_dict['datetime'] = int(
                    time.mktime(time.strptime(post_time, '%Y-%m-%d %H:%M:%S'))) - time.timezone

            elif temp_dict['datetime'] == 'Published':
                temp_dict['datetime'] = None

            elif temp_dict['datetime'].endswith('d'):
                post_time = datetime.datetime.now() - datetime.timedelta(
                    days=int(temp_dict['datetime'].replace('d', '')))
                post_time = post_time.strftime('%Y-%m-%d %H:%M:%S')

                # Convert from human readable date to epoch
                temp_dict['datetime'] = int(
                    time.mktime(time.strptime(post_time, '%Y-%m-%d %H:%M:%S'))) - time.timezone

            elif temp_dict['datetime'].endswith('w'):
                post_time = datetime.datetime.now() - datetime.timedelta(
                    weeks=int(temp_dict['datetime'].replace('w', '')))
                post_time = post_time.strftime('%Y-%m-%d %H:%M:%S')

                # Convert from human readable date to epoch
                temp_dict['datetime'] = int(
                    time.mktime(time.strptime(post_time, '%Y-%m-%d %H:%M:%S'))) - time.timezone

            elif temp_dict['datetime'].endswith('mo'):
                temp_dict['datetime'] = int(temp_dict['datetime'].replace('mo', '')) * 4
                post_time = datetime.datetime.now() - datetime.timedelta(
                    weeks=int(temp_dict['datetime']))
                post_time = post_time.strftime('%Y-%m-%d %H:%M:%S')

                # Convert from human readable date to epoch
                temp_dict['datetime'] = int(
                    time.mktime(time.strptime(post_time, '%Y-%m-%d %H:%M:%S'))) - time.timezone

            elif temp_dict['datetime'] == 'now':
                temp_dict['datetime'] = int(time.time())

            try:
                temp_dict['content'] = each_element.find('div', class_='feed-shared-text__text-view').text
                temp_dict['type'] = 'status'
            except AttributeError:
                temp_dict['content'] = None

            try:
                reactions = each_element.find('ul',
                                              class_='social-details-social-counts--justified social-details-social-counts ember-view').text
                try:
                    temp_dict['comments'] = int(reactions.replace(',', '').split('Comments\n')[1].split()[0])
                except:
                    temp_dict['comments'] = None
                try:
                    temp_dict['likes'] = int(reactions.replace(',', '').split('Reactions on')[0].split('\n')[-1])
                except:
                    temp_dict['likes'] = None

            # posts which have no reactions
            except AttributeError:
                temp_dict['comments'] = None
                temp_dict['likes'] = None
            # try:
            #     temp_dict['thumbnail'] = each_element.find('div', class_='feed-shared-article--with-large-image').img['src']
            #     temp_dict['type'] = 'link'
            #     temp_dict['url'] = each_element.find('div', class_='feed-shared-article--with-large-image').find(
            #         'a', {"data-control-name": "uptime_durationarticle_image"})['href']
            # except:
            #     temp_dict['thumbnail'] = None
            # try:
            #     te = each_element.find('div', class_='feed-shared-mini-update-v2__reshared-content').find('div', class_='relative')
            #     print(te)
            # except:
            #     pass
            # for i in temp_dict['thumbnail']:
            #     print(i)
            # print('@@@@@@@@@@@@')

            # type of post(videos, images, links etc...)
            try:
                img1 = each_element.find('div',
                                         class_='feed-shared-mini-update-v2__reshared-content feed-shared-image feed-shared-image--single-image ember-view').img
                # try:
                #     temp_dict['thumbnail'] = img1['src']
                # except:
                #     temp_dict['thumbnail'] = None
                try:
                    image_url = img1['src']
                    minio_url = minio_push.start_uploading([image_url], 'linkedin-service')
                    for i in minio_url:
                        if i['status'] == 200:
                            temp_dict['thumbnail'] = i['file_url']
                        else:
                            raise Exception('image not found')

                except (KeyError, TypeError):
                    temp_dict['thumbnail'] = None

                temp_dict['type'] = 'image'
                # print('****')
            except:
                pass
            try:
                img2 = each_element.find('div',
                                         class_='feed-shared-update-v2__content feed-shared-image feed-shared-image--single-image ember-view').img
                # try:
                #     temp_dict['thumbnail'] = img2['src']
                # except:
                #     temp_dict['thumbnail'] = None
                try:
                    image_url = img2['src']
                    minio_url = minio_push.start_uploading([image_url], 'linkedin-service')
                    for i in minio_url:
                        if i['status'] == 200:
                            temp_dict['thumbnail'] = i['file_url']
                        else:
                            raise Exception('image not found')

                except (KeyError, TypeError):
                    temp_dict['thumbnail'] = None

                temp_dict['type'] = 'image'
                # print('@@@@')
            except:
                pass
            try:
                img3 = each_element.find('div',
                                         class_='feed-shared-update-v2__content feed-shared-image feed-shared-image--multi-image feed-shared-image--has-two-images ember-view').img
                # try:
                #     temp_dict['thumbnail'] = img3['src']
                # except:
                #     temp_dict['thumbnail'] = None
                try:
                    image_url = img3['src']
                    minio_url = minio_push.start_uploading([image_url], 'linkedin-service')
                    for i in minio_url:
                        if i['status'] == 200:
                            temp_dict['thumbnail'] = i['file_url']
                        else:
                            raise Exception('image not found')

                except (KeyError, TypeError):
                    temp_dict['thumbnail'] = None
                temp_dict['type'] = 'image'
                # print('####')
            except:
                pass

            try:
                # temp_dict['url'] = each_element.find('div', class_='video-s-loader__video-components-container').find(
                #     'video')['src']

                temp_dict['thumbnail'] = each_element.find(
                    'div', class_='video-s-loader__video-components-container').find('video')['poster']

                image_url = temp_dict['thumbnail']
                minio_url = minio_push.start_uploading([image_url], 'linkedin-service')

                for i in minio_url:
                    if i['status'] == 200:
                        temp_dict['thumbnail'] = i['file_url']
                    else:
                        raise Exception('image not found')
                temp_dict['type'] = 'video'
            except:
                pass

            try:
                # temp_dict['url'] = each_element.find(
                #     'article', class_='feed-shared-update-v2__content feed-shared-article ember-view').a['href']

                try:
                    link_image = each_element.find(
                        'article', class_='feed-shared-update-v2__content feed-shared-article ember-view').img
                    # try:
                    #     temp_dict['thumbnail'] = link_image['src']
                    # except:
                    #     temp_dict['thumbnail'] = None
                    try:
                        image_url = link_image['src']
                        minio_url = minio_push.start_uploading([image_url], 'linkedin-service')
                        for i in minio_url:
                            if i['status'] == 200:
                                temp_dict['thumbnail'] = i['file_url']
                            else:
                                raise Exception('image not found')

                    except (KeyError, TypeError):
                        temp_dict['thumbnail'] = None
                except:
                    temp_dict['thumbnail'] = None
                temp_dict['type'] = 'link'
            except:
                try:
                    # temp_dict['url'] = each_element.find(
                    #     'article', class_='feed-shared-mini-update-v2__reshared-content  feed-shared-article ember-view').a['href']
                    try:
                        link_image2 = each_element.find('article',
                                                        class_='feed-shared-mini-update-v2__reshared-content  feed-shared-article ember-view').img
                        # try:
                        #     temp_dict['thumbnail'] = link_image2['src']
                        # except:
                        #     temp_dict['thumbnail'] = None
                        try:
                            image_url = link_image2['src']
                            minio_url = minio_push.start_uploading([image_url], 'linkedin-service')
                            for i in minio_url:
                                if i['status'] == 200:
                                    temp_dict['thumbnail'] = i['file_url']
                                else:
                                    raise Exception('image not found')

                        except (KeyError, TypeError):
                            temp_dict['thumbnail'] = None
                    except:
                        temp_dict['thumbnail'] = None
                    temp_dict['type'] = 'link'
                except:
                    pass

            # '//div[@class="feed-shared-update-v2__content feed-shared-image feed-shared-image--multi-image feed-shared-image--has-two-images ember-view"]'
            # '//div[@class="feed-shared-update-v2__content feed-shared-image feed-shared-image--single-image ember-view"]'
            # 'feed-shared-mini-update-v2__reshared-content  feed-shared-image feed-shared-image--single-image ember-view'

            print(temp_dict)

            redis_obj.publish(client_id, json.dumps(temp_dict))
            # print(each_element)
            self.c += 1

    def post_process(self, redis_obj, client_id, channel_obj):

        count = 0
        condition = True
        while condition:
            start_from = self.c
            print(start_from)
            try:
                self.parser(start_from, redis_obj, client_id, channel_obj)

                count += 1

                if self.process_loading():
                    if count == 11:
                        condition = False
                        redis_obj.publish(client_id, 'EOF')
                        channel_obj.unsubscribe(client_id)
                        self.driver.quit()
                    else:
                        continue
                else:
                    condition = False
                    redis_obj.publish(client_id, 'EOF')
                    channel_obj.unsubscribe(client_id)
                    self.driver.quit()
            except:
                return 'error in script'

        print(self.c)

        return

    # ----------------------------------------------------------------
    def get_posts(self, client_id, redis_obj, channel_obj):
        # process = self.post_process(index_to_process, redis_obj, client_id, channel_obj)
        process = self.post_process(redis_obj, client_id, channel_obj)
        if process == 'error in script':
            redis_obj.publish(client_id, 'EOF')
            channel_obj.unsubscribe(client_id)
        #     driver.close()
        #     driver.quit()
        #     return
        #
        # else:
        #     self.get_posts(driver, client_id, redis_obj, channel_obj, index_to_process=process)

    def search(self, q, time_duration=None):

        if time_duration:

            if time_duration == 'past_day':
                time_duration = 'past-24h'
            elif time_duration == 'past_week':
                time_duration = 'past-week'
            elif time_duration == 'past_month':
                time_duration = 'past-month'

            url = f"https://www.linkedin.com/search/results/content/?keywords={quote(q)}&origin=FACETED_SEARCH&recency={time_duration}"
            print(url)
        else:
            url = f"https://www.linkedin.com/search/results/content/?keywords={quote(q)}&origin=SWITCH_SEARCH_VERTICAL"
            print(url)

        self.driver.get(url)

        soup1 = BeautifulSoup(self.driver.page_source, 'lxml')
        # print(soup1.prettify())
        try:
            soup1.find('ul', class_='search-results__list').find_all('li', class_="search-content__result")

            selenium_session_id = self.driver.session_id
            client_id, redis_obj, channel_obj = self.redis_channel(selenium_session_id)
            # print(client_id, redis_obj, channel_obj)

            t = multiprocessing.Process(target=self.get_posts, args=(client_id, redis_obj, channel_obj))
            t.start()

            return {"channel_id": client_id}

        except AttributeError as e:
            print(e)
            self.driver.quit()
            return {"message": "no data found"}


if __name__ == '__main__':

    obj = SearchClass()
    print(obj.search(q="alexa ferna", time_duration="past_day"))

# Juha Sipilä
# Владимир Путин
# Nguyễn Xuân Phúc