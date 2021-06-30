import sys
import time
import json
from modules.caps_client import CapsClient
import indicoio
import requests
import multiprocessing
import redis
from time import sleep
from config import Config
from modules import minio_push
from modules.utils import date_formatter


class TwitterClass:

    def __init__(self):

        indicoio.config.api_key = CapsClient().get_credential_random('indico', 'api_key')['api_key']['access_token']
        # cred = CapsClient().get_credential_random('twitter')['api_key']

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
        client_id = 'twitter_search_service_' + selenium_session
        p = r.pubsub()  # pubsub object
        p.subscribe(client_id)
        return client_id, r, p

    def _jsonconvetor(self, tweets, client_id, redis_obj):
        # print(tweets)

        temp_dict = dict()

        temp_dict['url'] = f"https://twitter.com/{tweets['user']['screen_name']}/status/{tweets['id']}"

        try:
            if tweets['retweeted_status']:

                temp_dict['source'] = tweets['retweeted_status']['source'].split('rel="nofollow">')[1].replace('</a>', '')

                temp_dict['content'] = tweets['retweeted_status']['text']
                temp_dict['polarity'] = self.indico_sentiment(temp_dict['content'])

                temp_dict['hashtags'] = [i['text'] for i in tweets['retweeted_status']['entities']['hashtags']]
                if temp_dict['hashtags']:
                    pass
                else:
                    temp_dict['hashtags'] = None

                temp_dict['linked_url'] = [i['expanded_url'] for i in tweets['retweeted_status']['entities']['urls']]
                if temp_dict['linked_url']:
                    pass
                else:
                    temp_dict['linked_url'] = None

                temp_dict['mentions'] = [{'name': i['name'], 'username': i['screen_name'], 'userid': i['id']} for i in
                                         tweets['retweeted_status']['entities']['user_mentions']]
                if temp_dict['mentions']:
                    pass
                else:
                    temp_dict['mentions'] = None

                datetime_string = tweets['retweeted_status']['created_at']
                temp_dict['datetime'] = date_formatter(datetime_string)

                # author details
                temp_dict['author_userid'] = tweets['retweeted_status']['user']['id']
                temp_dict['author_name'] = tweets['retweeted_status']['user']['name']
                # temp_dict['author_image'] = tweets['retweeted_status']['user']['profile_image_url']
                try:
                    image_url = tweets['retweeted_status']['user']['profile_image_url']
                    minio_url = minio_push.start_uploading([image_url], 'twitter-service')
                    for i in minio_url:
                        if i['status'] == 200:
                            temp_dict['author_image'] = i['file_url']
                        else:
                            raise Exception('image not found')
                except:
                    temp_dict['author_image'] = None

                temp_dict['author_username'] = tweets['retweeted_status']['user']['screen_name']
                temp_dict['author_location'] = tweets['retweeted_status']['user']['location']
                temp_dict['description'] = tweets['retweeted_status']['user']['description']
                temp_dict['followers'] = tweets['retweeted_status']['user']['followers_count']
                temp_dict['following'] = tweets['retweeted_status']['user']['friends_count']
                join_string = tweets['retweeted_status']['user']['created_at']
                temp_dict['joined'] = date_formatter(join_string)

                temp_dict['author_likes'] = tweets['retweeted_status']['user']['favourites_count']
                temp_dict['verified'] = tweets['retweeted_status']['user']['verified']
                temp_dict['author_tweets'] = tweets['retweeted_status']['user']['statuses_count']
                temp_dict['tweets_language'] = tweets['retweeted_status']['user']['lang']
                temp_dict['retweets'] = tweets['retweeted_status']['retweet_count']
                temp_dict['likes'] = tweets['retweeted_status']['favorite_count']

                # attached media such as videos, images
                try:
                    temp_dict['type'] = tweets['retweeted_status']['extended_entities']['media'][0]['type']
                    # temp_dict['thumbnail'] = tweets['retweeted_status']['extended_entities']['media'][0]['media_url']

                    image_url = tweets['retweeted_status']['extended_entities']['media'][0]['media_url']
                    minio_url = minio_push.start_uploading([image_url], 'twitter-service')
                    for i in minio_url:
                        if i['status'] == 200:
                            temp_dict['thumbnail'] = i['file_url']
                        else:
                            raise Exception('image not found')

                except KeyError:
                    temp_dict['thumbnail'] = None
                    temp_dict['type'] = None

        except KeyError:

            temp_dict['source'] = tweets['source'].split('rel="nofollow">')[1].replace('</a>', '')
            temp_dict['content'] = tweets['text']
            temp_dict['polarity'] = self.indico_sentiment(temp_dict['content'])
            datetime_string = tweets['created_at']
            temp_dict['datetime'] = date_formatter(datetime_string)

            temp_dict['hashtags'] = [i['text'] for i in tweets['entities']['hashtags']]
            if temp_dict['hashtags']:
                pass
            else:
                temp_dict['hashtags'] = None

            temp_dict['linked_url'] = [i['expanded_url'] for i in tweets['entities']['urls']]
            if temp_dict['linked_url']:
                pass
            else:
                temp_dict['linked_url'] = None

            temp_dict['mentions'] = [{'name': i['name'], 'username': i['screen_name'], 'userid': i['id']} for i in
                                     tweets['entities']['user_mentions']]
            if temp_dict['mentions']:
                pass
            else:
                temp_dict['mentions'] = None

            # author details
            temp_dict['author_userid'] = tweets['user']['id']
            temp_dict['author_name'] = tweets['user']['name']
            # temp_dict['author_image'] = tweets['user']['profile_image_url']

            try:
                image_url = tweets['user']['profile_image_url']
                minio_url = minio_push.start_uploading([image_url], 'twitter-service')
                for i in minio_url:
                    if i['status'] == 200:
                        temp_dict['author_image'] = i['file_url']
                    else:
                        raise Exception('image not found')
            except:
                temp_dict['author_image'] = None

            temp_dict['author_username'] = tweets['user']['screen_name']
            temp_dict['author_location'] = tweets['user']['location']
            temp_dict['description'] = tweets['user']['description']
            temp_dict['followers'] = tweets['user']['followers_count']
            temp_dict['following'] = tweets['user']['friends_count']
            join_string = tweets['user']['created_at']
            temp_dict['joined'] = date_formatter(join_string)

            temp_dict['likes'] = tweets['user']['favourites_count']
            temp_dict['verified'] = tweets['user']['verified']
            temp_dict['author_tweets'] = tweets['user']['statuses_count']
            temp_dict['tweets_language'] = tweets['user']['lang']
            temp_dict['retweets'] = tweets['retweet_count']
            temp_dict['likes'] = tweets['favorite_count']

            # attached media such as videos, images
            try:
                temp_dict['type'] = tweets['extended_entities']['media'][0]['type']
                # temp_dict['thumbnail'] = tweets['extended_entities']['media'][0]['media_url']

                image_url = tweets['extended_entities']['media'][0]['media_url']
                minio_url = minio_push.start_uploading([image_url], 'twitter-service')
                for i in minio_url:
                    if i['status'] == 200:
                        temp_dict['thumbnail'] = i['file_url']
                    else:
                        raise Exception('image not found')

            except KeyError:
                temp_dict['thumbnail'] = None
                temp_dict['type'] = None

        print(temp_dict)
        redis_obj.publish(client_id, json.dumps(temp_dict))
        return
        # temp_dict['content'] = tweets['text']
        # # process source text
        # temp_dict['source'] = tweets['source'].split('rel="nofollow">')[1].replace('</a>', '')
        # temp_dict['hashtags'] = [i['text'] for i in tweets['entities']['hashtags']]
        # temp_dict['author_username'] = [i['screen_name'] for i in tweets['entities']['user_mentions']]
        # temp_dict['author_name'] = [i['name'] for i in tweets['entities']['user_mentions']]
        # try:
        #     temp_dict['thumbnail'] = tweets['entities']['media'][0]['media_url']
        #     temp_dict['url'] = tweets['entities']['media'][0]['url']
        #     temp_dict['type'] = tweets['entities']['media'][0]['type']
        # except KeyError:
        #     pass
        #
        # try:
        #     temp_dict['thumbnail'] = tweets['extended_entities']['media'][0]['media_url']
        #     temp_dict['url'] = tweets['extended_entities']['media'][0]['url']
        #     temp_dict['type'] = tweets['extended_entities']['media'][0]['type']
        #     temp_dict['video_duration'] = tweets['extended_entities']['media'][0]['video_info']['duration_millis']
        #     temp_dict['author_name'] = tweets['extended_entities']['media'][0]['additional_media_info']['source_user']['name']
        #     temp_dict['author_username'] = tweets['extended_entities']['media'][0]['additional_media_info']['source_user']['screen_name']
        #     temp_dict['location'] = tweets['extended_entities']['media'][0]['additional_media_info']['source_user']['location']
        #     temp_dict['description'] = tweets['extended_entities']['media'][0]['additional_media_info']['source_user']['description']
        #     temp_dict['linked_url'] = tweets['extended_entities']['media'][0]['additional_media_info']['source_user']['url']
        #     temp_dict['followers'] = tweets['extended_entities']['media'][0]['additional_media_info']['source_user']['followers_count']
        #     temp_dict['following'] = tweets['extended_entities']['media'][0]['additional_media_info']['source_user']['friends_count']
        #     temp_dict['joined'] = tweets['extended_entities']['media'][0]['additional_media_info']['source_user']['created_at']
        #     temp_dict['likes'] = tweets['extended_entities']['media'][0]['additional_media_info']['source_user']['favourites_count']
        #     temp_dict['verified'] = tweets['extended_entities']['media'][0]['additional_media_info']['source_user']['verified']
        #     temp_dict['tweets'] = tweets['extended_entities']['media'][0]['additional_media_info']['source_user']['statuses_count']
        # except KeyError:
        #     pass
        #
        #
        # print(temp_dict)

    def parser(self, list_of_posts, client_id, redis_obj, channel_obj):
        print(len(list_of_posts))
        # print(list_of_posts)
        count = 0
        sleep(3)
        for each_post in list_of_posts:
            # print(each_post)
            self._jsonconvetor(each_post, client_id, redis_obj)
            count += 1

        if len(list_of_posts) == count:
            redis_obj.publish(client_id, 'EOF')
            channel_obj.unsubscribe(client_id)

    def twitter_search(self, params):

        url = 'https://api.twitter.com/1.1/search/tweets.json'

        headers = {'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANrG%2FAAAAAAAXrXhkOqmVSoGYjB55n2mFINLMPo%3DuoXEp6TeXgmMZabN050B1lv1rFF07uhWI938bRfH717NxOW4Ak'}
        req = requests.session()
        response = req.get(url=url, params=params, headers=headers)

        # print(response.json())

        if response.json()['statuses']:
            # print(response.json()['statuses'])

            session_id = str(req).replace('<requests.sessions.Session object at ', '')
            client_id, redis_obj, channel_obj = self.redis_channel(session_id)

            t = multiprocessing.Process(target=self.parser,
                                        args=(response.json()['statuses'], client_id, redis_obj, channel_obj))
            t.start()

            return {"channel_id": client_id}

        else:
            return {'message': 'no data found'}

    def processor(self, q=None, or_=None, and_=None, exclude=None, media=None, from_account=None, hashtag=None,
                  from_date=None, to_date=None, lang=None, result_type=None, handle=None, to_account=None):

        query = ''
        if q:
            query += q
        if and_:
            query += ' AND '+and_
        if or_:
            query += ' OR '+or_
        if exclude:
            query += ' -'+exclude
        if hashtag:
            query += ' #'+hashtag
        if handle:
            query += ' @'+handle

        # -----------------------------

        params = {'count': 100}

        if query:
            params['q'] = query
        if from_account:
            params['from'] = from_account
        if to_account:
            params['to'] = to_account
        if media:
            params['filter'] = media
        if from_date:
            params['since'] = time.strftime("%Y-%m-%d", time.localtime(from_date))
        if to_date:
            params['until'] = time.strftime("%Y-%m-%d", time.localtime(from_date))
        if lang:
            params['lang'] = lang
        if result_type:
            params['result_type'] = result_type

        print(params)

        return self.twitter_search(params)


if __name__ == '__main__':
    obj = TwitterClass()
    # print(obj.profiletweets('realdonaldtrump', 50))
    # print(obj.hashtags('politico', 34))
    # print(obj.handlertweets('realdonaldtrump', 100))

    # print(obj.query_name(20, q='trump', media='videos', from_date=1545322834, to_date=1555322834, exclude='donald', from_account='bbc.com', lang='en'))
    print(obj.processor(q='#metoo AND #FBR'))
