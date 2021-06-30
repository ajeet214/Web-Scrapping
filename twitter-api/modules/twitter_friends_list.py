import json
from time import sleep
import multiprocessing
import random
import indicoio
import requests
from requests_oauthlib import OAuth1
import redis
from config import Config
from modules.caps_client import CapsClient, CredentialType, CredentialPlatform
from modules.utils import date_formatter
from modules import minio_push


class FriendsProfile:

    def __init__(self):

        obj = CapsClient()
        indicoio.config.api_key = obj.get_credential_random(CredentialPlatform.INDICO, CredentialType.API_KEY)['api_key']['access_token']

        '''fetching random credentials'''
        self.cred = random.choice(obj.get_credential_random(CredentialPlatform.TWITTER, CredentialType.API_KEY)['api_key'])
        print('consumer_key:', self.cred['consumer_key'])

        self.auth = OAuth1(self.cred['consumer_key'], self.cred['consumer_secret'], self.cred['access_token'],
                      self.cred['access_token_secret'])

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
        client_id = 'twitter_friend_profile_' + selenium_session
        p = r.pubsub()  # pubsub object
        p.subscribe(client_id)
        return client_id, r, p

    def parser(self, profileobj, client_id, redis_obj):

        for each_profile in profileobj['users']:
            temp_dict = dict()

            # print(each_profile)
            temp_dict['userid'] = each_profile['id']
            temp_dict['name'] = each_profile['name']
            temp_dict['username'] = each_profile['screen_name']
            temp_dict['url'] = 'https://twitter.com/'+each_profile['screen_name']
            temp_dict['location'] = each_profile['location']
            if not temp_dict["location"]:
                temp_dict["location"] = None

            temp_dict['linked_url'] = each_profile['url']
            temp_dict["verified"] = each_profile['verified']
            temp_dict['description'] = each_profile['description']
            if not temp_dict["description"]:
                temp_dict["description"] = None

            temp_dict['followers'] = each_profile['followers_count']
            temp_dict['following'] = each_profile['friends_count']
            if 'sticky/default_profile_images' in each_profile['profile_image_url_https']:
                temp_dict['image'] = None
            else:
                image_url = each_profile['profile_image_url_https'].replace('_normal', '')
                minio_url = minio_push.start_uploading([image_url], 'twitter-service')
                for i in minio_url:
                    if i['status'] == 200:
                        temp_dict['image'] = i['file_url']
                    else:
                        raise Exception('image not found')

            temp_dict['tweets'] = each_profile['statuses_count']
            temp_dict["profile_created_at"] = date_formatter(each_profile['created_at'])

            # temp['polarity'] = self.indico_sentiment(each_profile['description'])

            temp_dict['type'] = 'identity'
            #
            print(temp_dict)
            redis_obj.publish(client_id, json.dumps(temp_dict))
        if profileobj['next_cursor']:
            return True, profileobj['next_cursor']
        else:
            return False, None

    def test(self, next_cursor, username, client_id, redis_obj, channel_obj):

        url = f'https://api.twitter.com/1.1/friends/list.json?cursor={next_cursor}&screen_name={username}&skip_status=true&include_user_entities=false&count=199'
        try:
            r = requests.get(url, auth=self.auth)
            # print(r.json())
            return r.json()
        except :

            redis_obj.publish(client_id, 'EOF')
            channel_obj.unsubscribe(client_id)
            raise ConnectionError

    def dataprocessing(self, friend_object, username, client_id, redis_obj, channel_obj):
        sleep(1)
        next_page, next_cursor = self.parser(friend_object, client_id, redis_obj)
        # print(next_page, next_cursor)

        if next_page:

            count = 0
            condition = True
            while condition:
                count += 1
                print('in loop')
                next_page, next_cursor = self.parser(
                    self.test(next_cursor, username, client_id, redis_obj, channel_obj), client_id, redis_obj)
                if next_page:
                    pass
                else:
                    condition = False

        redis_obj.publish(client_id, 'EOF')
        channel_obj.unsubscribe(client_id)

    def friendsprofile(self, username):

        url = f'https://api.twitter.com/1.1/friends/list.json?cursor=-1&screen_name={username}&skip_status=true&include_user_entities=false&count=199'

        try:
            res = requests.get(url, auth=self.auth)

            if res.status_code == 200:
                session_id = str(random.random).replace(' ', '')
                client_id, redis_obj, channel_obj = self.redis_channel(session_id)

                t = multiprocessing.Process(target=self.dataprocessing,
                                            args=(res.json(), username, client_id, redis_obj, channel_obj))
                t.start()

                return {"channel_id": client_id}

            else:
                return {"message": 'no data found'}

        except requests.exceptions.ConnectionError:
            return {"message": 'Max retries exceeded'}


if __name__ == '__main__':
    tmp = FriendsProfile()
    # print((tmp.profilefetcher("realdonaldtrump")))
    print(tmp.friendsprofile("martin"))

