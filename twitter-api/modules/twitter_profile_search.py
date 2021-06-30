from sys import exc_info
import sys
import tweepy
import time
import json
from requests_futures.sessions import FuturesSession
from concurrent.futures import ThreadPoolExecutor
import demjson
from modules.caps_client import CapsClient, CredentialType, CredentialPlatform
from credentials import TwitterKeys, google_keys
import indicoio
import random
import multiprocessing
import redis
from config import Config
from modules import minio_push


class TwitterSearch:

    def __init__(self):

        obj = CapsClient()
        indicoio.config.api_key = obj.get_credential_random(CredentialPlatform.INDICO, CredentialType.API_KEY)['api_key']['access_token']
        self.session = FuturesSession(executor=ThreadPoolExecutor(max_workers=5))

        cred = random.choice(obj.get_credential_random(CredentialPlatform.TWITTER, CredentialType.API_KEY)['api_key'])

        try:
            self.auth = tweepy.OAuthHandler(cred['consumer_key'], cred['consumer_secret'])
            self.auth.set_access_token(cred['access_token'], cred['access_token_secret'])
            self.api = tweepy.API(self.auth)
        except:
            print("error::init>>", sys.exc_info()[1])

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
        client_id = 'twitter_profile_search_service_' + selenium_session
        p = r.pubsub()  # pubsub object
        p.subscribe(client_id)
        return client_id, r, p

    # data modifier
    def _jsonconvetor(self, tweets):
        # print(tweets)
        tempdict = dict()
        temp = dict()
        # tempdict["postContent"] = tweets.description
        # tempdict['polarity'] = self.indico_sentiment(tweets.description)

        # tempdict["followers_count"] = tweets.followers_count
        # tempdict["location"] = tweets.location
        # tempdict["name"] = tweets.name
        # # tempdict["lastName"] = None
        # tempdict["authorId"] = tweets.screen_name

        temp = tweets._json['created_at']
        var = [(1, 'Jan'), (2, 'Feb'), (3, 'Mar'), (4, 'Apr'), (5, 'May'), (6, 'Jun'), (7, 'Jul'), (8, 'Aug'), (
            9, 'Sep'), (10, 'Oct'), (11, 'Nov'), (12, 'Dec')]
        m = temp[4:7]
        for i in var:
            if i[1] == m:
                m = str(i[0])
        tempdict["datetime"] = int(time.mktime(time.strptime(temp[-4:]+'-'+m+'-'+temp[8:10]+' '+temp[11:19],
                                                             '%Y-%m-%d %H:%M:%S'))) - time.timezone

        tempdict["description"] = tweets._json['description']
        if not tempdict["description"]:
            tempdict["description"] = None

        tempdict["likes"] = tweets._json['favourites_count']
        tempdict["followers"] = tweets._json['followers_count']
        tempdict['following'] = tweets._json['friends_count']
        tempdict["username"] = tweets._json['screen_name']
        tempdict["userid"] = tweets._json['id']
        tempdict['url'] = 'https://twitter.com/{}'.format(tempdict["username"])

        # tempdict["geo_enabled"] = tweets._json['geo_enabled']
        # tempdict["id"] = tweets._json['id']
        # tempdict["listed_count"] = tweets._json['listed_count']
        tempdict["location"] = tweets._json['location']
        if not tempdict["location"]:
            tempdict["location"] = None

        tempdict["name"] = tweets._json['name']
        # try:
        #     tempdict["profile_banner_url"] = tweets._json['profile_banner_url']
        # except:
        #     pass
        tempdict["image"] = tweets._json['profile_image_url']

        # enhancement in the image quality
        tempdict["image"] = tempdict["image"].replace('_normal.', '_400x400.').replace('_normal.', '_400x400.').replace(
            '_normal.', '_400x400.')

        # tempdict["profile_link_color"] = tweets._json['profile_link_color']
        # tempdict["profile_sidebar_border_color"] = tweets._json['profile_sidebar_border_color']
        # tempdict["profile_use_background_image"] = tweets._json['profile_use_background_image']

        tempdict["tweets"] = tweets._json['statuses_count']
        # tempdict["linked_url"] = tweets._json['url']
        try:
            tempdict["linked_url"] = tweets._json['entities']['url']['urls'][0]['expanded_url']
        except KeyError:
            tempdict["linked_url"] = None
        tempdict["verified"] = tweets._json['verified']

        return tempdict
        # print(tempdict)

    def get(self, tmp, client_id, redis_obj, channel_obj):
        time.sleep(1)

        # removing duplicate dict object
        temp = [dict(t) for t in {tuple(d.items()) for d in tmp}]
        # print(temp)
        location_list = []
        for i in temp:
            if i['location'] is not None:
                location_list.append((i['location'], i['username']))

        rs = []
        for u in location_list:
            rs.append((self.session.get('https://maps.google.com/maps/api/geocode/json?address=' + str(
                u[0]) + '&key=' + google_keys), u[0], u[1]))

        # print(rs)

        results = []
        for response in rs:

            try:
                r = response[0].result()
                lt = demjson.decode(r.content.decode('utf-8'))
                # print(lt)
                # print(lt['results'][0]['address_components'])
                temp_dict = {}

                for i in lt['results'][0]['address_components']:
                    if i['types'][0] == 'country':
                        # print(i['long_name'])
                        temp_dict['country_code'] = i['short_name']
                        temp_dict['country'] = i['long_name']
                        temp_dict['id'] = response[2]
                        temp_dict['location'] = response[1]
                        results.append(temp_dict)
                # print('**********')
                # print(temp_dict)
                if not temp_dict:
                    _dict = dict()
                    _dict['country'] = None
                    _dict['country_code'] = None
                    _dict['location'] = response[1]
                    _dict['id'] = response[2]
                    results.append(_dict)

            # when google geocode api sends error
            except IndexError:
                pass

        # print(results)

        final_list = []
        count = 0
        for i in range(len(temp)):
            final_dict = dict()

            final_dict['location'] = temp[i]['location']
            final_dict['description'] = temp[i]['description']
            final_dict['verified'] = temp[i]['verified']
            final_dict['datetime'] = temp[i]['datetime']
            final_dict['likes'] = temp[i]['likes']
            final_dict['following'] = temp[i]['following']
            final_dict['followers'] = temp[i]['followers']
            final_dict['name'] = temp[i]['name']
            # final_dict['image'] = temp[i]['image']
            final_dict['username'] = temp[i]['username']
            final_dict['userid'] = temp[i]['userid']
            final_dict['url'] = temp[i]['url']
            final_dict['posts'] = temp[i]['tweets']
            final_dict['linked_url'] = temp[i]['linked_url']
            # final_dict['polarity'] = temp[i]['polarity']
            final_dict['type'] = 'identity'
            final_dict['country'] = None
            final_dict['country_code'] = None

            # final_dict['country'] = results[i]['country']
            # final_dict['country_code'] = results[i]['country_code']
            for j in results:
                if j['id'] == temp[i]['username']:
                    final_dict['country'] = j['country']
                    final_dict['country_code'] = j['country_code']

            try:
                image_url = temp[i]['image']
                minio_url = minio_push.start_uploading([image_url], 'twitter-service')
                for i in minio_url:
                    if i['status'] == 200:
                        final_dict['image'] = i['file_url']
                    else:
                        raise Exception('image not found')
            except:
                final_dict['image'] = None

            # final_list.append(final_dict)
            print(final_dict)
            count += 1
            redis_obj.publish(client_id, json.dumps(final_dict))

        if count == len(temp):
            redis_obj.publish(client_id, 'EOF')
            channel_obj.unsubscribe(client_id)

    def profilesearch(self, q, limit=100):
        # if limit==None:
        #     limit=20
        tmp = []
        for users in tweepy.Cursor(self.api.search_users, q=q).items(limit=int(limit)):
            # print(users)
            # self._insetvalue(users)
            data = self._jsonconvetor(users)
            # print(data)
            tmp.append(data)

        if tmp:

            session_id = str(random.random).replace(' ', '')
            client_id, redis_obj, channel_obj = self.redis_channel(session_id)

            t = multiprocessing.Process(target=self.get,
                                        args=(tmp, client_id, redis_obj, channel_obj))
            t.start()

            return {"channel_id": client_id}


        else:
            return {'message': 'no data found'}


if __name__ == '__main__':
    obj = TwitterSearch()
    print(obj.profilesearch(q='bill gates'))

# eric freymond
# niger delta