import requests
from config import Config
import redis
from bs4 import BeautifulSoup
import multiprocessing
import json
import random
from urllib.parse import quote
from time import sleep
from modules import minio_push
from modules.caps_client import CapsClient, CredentialType
from modules import login_file


class ProfilePosts:

    def __init__(self, username, category):

        # self.proxy = self._get_proxy()
        login = login_file.Login()
        login.loginmethod()
        self.client = login.client

        soup = BeautifulSoup(self.client.get('https://www.linkedin.com/uas/login').text, 'lxml')
        self.csrf = soup.find('input', {"name": "csrfToken"})['value']
        # print(self.csrf)

        if category == 'all':
            self.moduleKey = 'member-activity'
            self.q = 'memberFeed'
        elif category == 'posts':
            self.moduleKey = 'member-shares'
            self.q = 'memberShareFeed'

        self.username = username
        res = self.client.get(f'https://www.linkedin.com/in/{username}/detail/recent-activity')
        # print(res.text)
        self.profile_urn = quote(
            res.text[res.text.find("urn:li:fs_profile:"):res.text.find("urn:li:fs_profile:") + 80].split('&')[0])
        # print(self.profile_urn)

        self.headers = {"csrf-token": self.csrf,
         "referer": f"https://www.linkedin.com/in/{username}/detail/recent-activity/",
         "x-li-lang": "en_US",
         "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
         "x-li-track": '{"clientVersion":"1.3.3248","osName":"web","timezoneOffset":-7,"deviceFormFactor":"DESKTOP","mpName":"voyager-web"}',
         "accept-language": 'en-US,en;q=0.9'
                        }

        cookies = CapsClient().get_credential_random(platform='instagram', type=CredentialType.COOKIES)['cookies']

        self.header = {
            "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36'
        }

    # random proxy based on chosen filters
    def _get_proxy(self):

        try:
            random_proxy = CapsClient().get_proxy_random(type='socks5')
            print(random_proxy)
            return "socks5://{}:{}".format(random_proxy['host'], random_proxy['port'])

        except:
            return 'socks5://45.76.44.175:4899'

    def redis_channel(self, selenium_session):

        # r = redis.Redis(host=self.redis_host, port=self.redis_port)
        r = redis.from_url("redis://{}".format(Config.REDIS_URI))
        client_id = 'profile_posts_' + selenium_session
        p = r.pubsub()  # pubsub object
        p.subscribe(client_id)
        return client_id, r, p

    def parser(self, raw_data, client_id, redis_obj):

        list_of_posts = raw_data['elements']
        for each_post in list_of_posts:

            temp_dict = dict()

            temp_dict['likes'] = each_post['socialDetail']['likes']['paging']['total']
            temp_dict['comments'] = each_post['socialDetail']['comments']['paging']['total']
            # temp_dict['action'] = each_post['header']['text']['attributes']['text']
            temp_dict['url'] = [i['url'] for i in each_post['updateMetadata']['actions'] if i['actionType'] == 'SHARE_VIA'][0]
            #
            try:
                temp_dict['author_name'] = each_post['actor']['name']['text']
                temp_dict['datetime'] = each_post['actor']['subDescription']['text']
                temp_dict['author_url'] = each_post['actor']['navigationContext']['actionTarget ']

                try:
                    temp_dict['author_image'] = each_post['actor']['image']['attributes'][0]['miniCompany']['logo']['com.linkedin.common.VectorImage']['rootUrl']+each_post['actor']['image']['attributes'][0]['miniCompany']['logo']['com.linkedin.common.VectorImage']['artifacts'][-1]['fileIdentifyingUrlPathSegment']
                    temp_dict['followers'] = each_post['actor']['followAction']['followingInfo']['followerCount']
                except KeyError:
                    temp_dict['author_image'] = each_post['actor']['image']['attributes'][0]['miniProfile']['picture']['com.linkedin.common.VectorImage']['rootUrl']+each_post['actor']['image']['attributes'][0]['miniProfile']['picture']['com.linkedin.common.VectorImage']['artifacts'][-1]['fileIdentifyingUrlPathSegment']
                    temp_dict['author_username'] = each_post['actor']['image']['attributes'][0]['miniProfile']['publicIdentifier']
                    temp_dict['author_occupation'] = each_post['actor']['image']['attributes'][0]['miniProfile']['occupation']

            except KeyError:
                pass

            try:
                temp_dict['thumbnail'] = each_post['content']['com.linkedin.voyager.feed.render.ArticleComponent'][
                    'largeImage']['attributes'][0]['imageUrl']
            except KeyError:
                try:
                    rooturl = [i['attributes'][0]['vectorImage']['rootUrl'] for i in each_post['content']['com.linkedin.voyager.feed.render.ImageComponent']['images']]

                    other_half = [j['attributes'][0]['vectorImage']['artifacts'][-1]['fileIdentifyingUrlPathSegment'] for j in each_post['content']['com.linkedin.voyager.feed.render.ImageComponent']['images']]

                    temp_dict['thumbnail'] = [rooturl[i]+other_half[i] for i in range(len(rooturl))]
                except KeyError:
                    temp_dict['thumbnail'] = None
            # temp_dict['title'] = each_post['content']['com.linkedin.voyager.feed.render.ArticleComponent']['title']['text']

            try:
                temp_dict['content'] = each_post['commentary']['text']['text']
            except KeyError:
                temp_dict['content'] = None


            # try:
            #     image_url = each_following['node']['profile_pic_url']
            #     minio_url = minio_push.start_uploading([image_url], 'instagram-service')
            #     for i in minio_url:
            #         if i['status'] == 200:
            #             temp_dict['image'] = i['file_url']
            #         else:
            #             raise Exception('image not found')
            # except:
            #     temp_dict['image'] = None

            print(temp_dict)
            redis_obj.publish(client_id, json.dumps(temp_dict))

        if raw_data['metadata']['paginationToken']:
            return True, raw_data['metadata']['paginationToken']
        else:
            return False, None

    def test(self, next_cursor, client_id, redis_obj, channel_obj):
        # print(next_cursor)

        url = f'https://www.linkedin.com/voyager/api/identity/profileUpdatesV2?count=90&includeLongTermHistory=true&moduleKey={self.moduleKey}%3Aphone&paginationToken={next_cursor}&profileUrn={self.profile_urn}&q={self.q}'

        try:
            posts = self.client.get(url, headers=self.headers)
            # print(posts.json())
            return posts.json()
        except requests.exceptions.ConnectionError:

            redis_obj.publish(client_id, 'EOF')
            channel_obj.unsubscribe(client_id)
            raise ConnectionError

    def pagination(self, json_data, client_id, redis_obj, channel_obj):
        # print('pagination starts')
        sleep(1)

        next_page, next_cursor = self.parser(json_data, client_id, redis_obj)

        if next_page:

            count = 0
            condition = True
            while condition:
                count += 1
                # print('in loop')
                next_page, next_cursor = self.parser(self.test(next_cursor, client_id, redis_obj, channel_obj), client_id, redis_obj)
                if next_page:
                    pass
                else:
                    condition = False

            if count == 3:

                redis_obj.publish(client_id, 'EOF')
                channel_obj.unsubscribe(client_id)

        redis_obj.publish(client_id, 'EOF')
        channel_obj.unsubscribe(client_id)

    def processor(self):

        url = f'https://www.linkedin.com/voyager/api/identity/profileUpdatesV2?count=90&includeLongTermHistory=true&moduleKey={self.moduleKey}%3Aphone&profileUrn={self.profile_urn}&q={self.q}'

        posts = self.client.get(url, headers=self.headers)

        data = posts.json()
        # print(data['elements'])

        if data['elements']:
            session_id = str(random.random).replace('<built-in method random of Random ', '')
            client_id, redis_obj, channel_obj = self.redis_channel(session_id)
            t = multiprocessing.Process(target=self.pagination,
                                        args=(data, client_id, redis_obj, channel_obj))
            t.start()

            return {"channel_id": client_id}
        else:
            return {"message": "no data found"}


if __name__ == '__main__':
    Obj = ProfilePosts(username='petyab', category='posts')
    print(Obj.processor())


# rumyana-vaseva
# petyab