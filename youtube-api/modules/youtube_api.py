import requests
import json
from modules.sentiment import SentimentAnalysis
import time
from modules.base_api import BaseApi
from credentials import creds
import indicoio
import asyncio
import concurrent.futures
from modules.caps_client import CapsClient


class YoutubeApi(BaseApi):

    # key = "AIzaSyCqXymDa4M2vvrtS3v4l7dn7uIODNNAGRU"
    def _get_credentials(self):
        # change url as per credentials reequired
        url = "http://credsnproxy/api/v1/google"
        try:
            req = requests.get(url=url)
            if req.status_code != 200:
                raise ValueError
            return req.json()
        except:
            # return fallback object
            return {
                "email": creds['email'],
                "password": creds['password'],
                "api_key": creds['google_api_key'],
                "proxy_host": "185.193.36.122",
                "proxy_port": "23343"
            }

    def __init__(self):

        self.obj = SentimentAnalysis()
        # self.indicoio = indicoio.config.api_key = 'a40c4ac2fdc7bcbd071772813b75244c'
        indicoio.config.api_key = CapsClient().get_credential_random('indico', 'api_key')['api_key']['access_token']
        self.key = self._get_credentials()['api_key']
        self.neg_count = 0
        self.neu_count = 0
        self.pos_count = 0
        self.url = "https://www.googleapis.com/youtube/v3/search?q=%s&key=%s&part=id,snippet&maxResults=40"
        self.social = "youtube"
        BaseApi.__init__(self, social=self.social)
        self.result_list = []

    def data_processor(self, i):
        # print(i)
        new_dict = dict()

        # new_dict['polarity'] = i['polarity']
        new_dict['content'] = i['snippet']['description']
        if not new_dict['content']:
            new_dict['content'] = None
            # new_dict['content'] = "null"
        new_dict['title'] = i['snippet']['title']
        new_dict['author_name'] = i['snippet']['channelTitle']
        new_dict['author_userid'] = i['snippet']['channelId']

        new_dict['author_url'] = 'https://www.youtube.com/channel/{}'.format(new_dict['author_userid'])
        new_dict['datetime'] = int(time.mktime(time.strptime(i['snippet']['publishedAt'][:-5].replace('T', ' '),
                                                              '%Y-%m-%d %H:%M:%S'))) - time.timezone
        new_dict['thumbnail'] = i['snippet']['thumbnails']['high']['url']

        try:
            new_dict['postid'] = i['id']['videoId']
            new_dict['url'] = 'https://www.youtube.com/watch?v={}'.format(new_dict['postid'])
            new_dict['type'] = 'video'
        except:
            new_dict['postid'] = None
            new_dict['url'] = None
            new_dict['type'] = 'page'

        self.result_list.append(new_dict)

        # new_dict['polarity'] = i['polarity']
        # try:
        #     new_dict['post_id'] = i['id']['videoId']
        #     new_dict['post_url'] = 'https://www.youtube.com/watch?v={}'.format(new_dict['post_id'])
        #
        # except:
        #     pass
        # new_dict['post_content'] = i['snippet']['description']
        # new_dict['post_title'] = i['snippet']['title']
        # new_dict['profile_name'] = i['snippet']['channelTitle']
        # new_dict['profile_id'] = i['snippet']['channelId']
        # new_dict['profile_url'] = 'https://www.youtube.com/channel/{}'.format(new_dict['profile_id'])
        # new_dict['post_time'] = int(time.mktime(time.strptime(i['snippet']['publishedAt'][:-5].replace('T', ' '),
        #                                                       '%Y-%m-%d %H:%M:%S'))) - time.timezone
        # new_dict['post_image'] = i['snippet']['thumbnails']['high']['url']
        # self.result_list.append(new_dict)

    def searchApi(self, query, stype=None):
        data = self.get_request(url=self.url % (query, self.key))
        # print(data)
        parsed = json.loads(data.decode())
        # print(parsed['items'])
        for item in parsed['items']:
            # print(item['snippet']['description'])
            # pol = self.obj.analize_sentiment(item['snippet']['description'])
            # pol = indicoio.sentiment(item['snippet']['description'])

            # item['polarity'] = pol
            # if pol > 0.5:
            #     item['polarity'] = 'positive'
            #     self.pos_count += 1
            # elif pol < 0.5:
            #     item['polarity'] = 'negative'
            #     self.neu_count += 1
            # else:
            #     item['polarity'] = 'neutral'
            #     self.neg_count += 1
            self.data_processor(item)

        # ps = self.pos_count
        # ng = self.neg_count
        # nu = self.neu_count
        # total = ps + ng + nu
        #
        # sentiments = dict()
        # sentiments["positive"] = ps
        # sentiments["negative"] = ng
        # sentiments["neutral"] = nu

        return self.result_list
                    # 'sentiments': sentiments,
                    # 'total': total


async def main(result_list):

    lst = []
    print(result_list)
    print(len(result_list))

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:

        loop = asyncio.get_event_loop()
        urls = result_list
        # print(urls)

        # futures = [loop.run_in_executor(executor, indicoio.sentiment, i['content'])for i in urls]
        futures = []
        for i in urls:
            if i['content'] is None:

                futures.append(loop.run_in_executor(executor, indicoio.sentiment, 'null'))
                pass
            else:
                futures.append(loop.run_in_executor(executor, indicoio.sentiment, i['content']))

        for response in await asyncio.gather(*futures):
            # print(response.text)
            lst.append(response)

    # for i in lst:
    #     print(i)
    print(lst)
    print(len(lst))
    for i in range(len(result_list)):

        if lst[i] > 0.5000000000000000:
            result_list[i]['polarity'] = 'positive'
        elif lst[i] == 0.031184496628274796:
            result_list[i]['polarity'] = 'neutral'
        elif lst[i] < 0.5000000000000000:
            result_list[i]['polarity'] = 'negative'

    # print(result_list)
    return result_list

if __name__ == '__main__':
    youtube = YoutubeApi()
    # print(youtube.searchApi('miller'))
    list_res = youtube.searchApi('miller')
    loop = asyncio.get_event_loop()
    print(loop.run_until_complete(main(list_res)))
    loop.close()

