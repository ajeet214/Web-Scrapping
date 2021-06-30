import requests
from credentials import google_api_key
from urllib.parse import urlencode
import asyncio
# from modules.sentiment import Sentiment_analysis
from modules.multi_lingual_sentiment import main
from config import Config
from modules.caps_client import CapsClient


class KnowledgeGraphSearch:

    def __init__(self):

        self.proxy = self._get_proxy()
        # self.neg_count = 0
        # self.neu_count = 0
        # self.pos_count = 0
        self.api_key = self._get_key()
        # self.obj = Sentiment_analysis()
        self.result_list = []

    def _get_proxy(self):

        try:
            random_proxy = CapsClient().get_proxy_random(type='socks5')
            print(random_proxy)
            return "socks5://{}:{}".format(random_proxy['host'], random_proxy['port'])

        except:
            return 'socks5://89.39.107.101:80'
            # '45.76.44.175:4899'

    def _get_key(self):

        url = "http://credsnproxy/api/v1/google"
        try:
            creds = requests.get(url=url).json()
            return creds['api_key']
        except:
            return google_api_key

    def dataprocessor(self, item):

        new_dict = dict()
        new_dict['score'] = item['resultScore']
        try:
            new_dict['linked_url'] = item['result']['url']
        except:
            new_dict['linked_url'] = None
        try:
            new_dict['profile_name'] = item['result']['name']
        except:
            new_dict['profile_name'] = None
        try:
            new_dict['description'] = item['result']['description']
        except:
            new_dict['description'] = None

        new_dict['category'] = item['result']['@type']
        new_dict['id'] = item['result']['@id']
        try:
            new_dict['profile_image'] = item['result']['image']['contentUrl']
            new_dict['image_url'] = item['result']['image']['url']
        except:
            new_dict['profile_image'] = None
            new_dict['image_url'] = None
        try:
            new_dict['content'] = item['result']['detailedDescription']['articleBody']
            new_dict['profile_url'] = item['result']['detailedDescription']['url']
        except:
            new_dict['content'] = None
            new_dict['profile_url'] = None
        # new_dict['polarity'] = item['polarity']
        self.result_list.append(new_dict)

    def knowledge_search(self, query, count):

        query = query
        service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
        params = {
            'query': query,
            'limit': count,
            'indent': True,
            'key': self.api_key,
        }

        header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
        proxy = {'http': "{}".format(self._get_proxy())}
        print(proxy)

        url = service_url + '?' + urlencode(params)
        # print(url)
        # response = json.loads(urlopen(url).read().decode('utf-8'))
        response = requests.get(url, headers=header, proxies=proxy)
        # print(response.json())
        response = response.json()
        polarity = {}

        try:
            for element in response['itemListElement']:
                # print(element)
                # try:
                #     t = element['result']['detailedDescription']['articleBody']
                #
                #     pol = self.obj.analize_sentiment(t)
                #
                #     if pol == 1:
                #         element['polarity'] = 'positive'
                #         self.pos_count += 1
                #     elif pol == -1:
                #         element['polarity'] = 'negative'
                #         self.neg_count += 1
                #     else:
                #         element['polarity'] = 'neutral'
                #         self.neu_count += 1
                #
                #     # element['polarity'] = pol
                # except:
                #     # element['polarity'] = 0
                #     element['polarity'] = 'neutral'
                #     self.neu_count += 1

                self.dataprocessor(element)

            # print(response['itemListElement'])

            # ps = self.pos_count
            # ng = self.neg_count
            # nu = self.neu_count
            # total = ps+ng+nu
            #
            # Sentiments = dict()
            # Sentiments["positive"] = ps
            # Sentiments["negative"] = ng
            # Sentiments["neutral"] = nu

            # return {'data':
            #             {
            #                 'results': self.result_list,
            #                 'sentiments': Sentiments,
            #                 'total': count
            #             }
            #         }
            return self.result_list
        except KeyError:
            return 'limit exceeded'

    def processor(self, query, limit):
        OBJ = KnowledgeGraphSearch()
        # print(youtube.searchApi('miller'))
        list_res = OBJ.knowledge_search(query, limit)
        print(list_res)
        if list_res == "limit exceeded":
            return {"message": "limit exceeded"}

        elif len(list_res) == 0:
            return {"message": "no data found"}

        # loop = asyncio.get_event_loop()
        """loop = asyncio.get_event_loop()
           with:
           
           loop = asyncio.new_event_loop()
           asyncio.set_event_loop(loop)"""

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # print(loop.run_until_complete(OBJ.main(list_res)))
        return {"data": loop.run_until_complete(main(list_res))}


if __name__ == '__main__':
    obj = KnowledgeGraphSearch()
#     # print(obj.knowledge_search('Nguyễn Xuân Phúc', 40))
    print(obj.processor('paul walker', 40))
