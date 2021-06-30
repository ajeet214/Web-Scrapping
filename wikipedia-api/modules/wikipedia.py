from flask import json
import requests
import asyncio
from modules.multi_lingual_sentiment import main
from modules.caps_client import CapsClient


class Wikipedia:

    def __init__(self):

        self.proxy = self._get_proxy()
        self.api_base = 'https://en.wikipedia.org/w/api.php?'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0'
        }
        self.main = main

    def _get_proxy(self):
        ob = CapsClient()
        try:
            # req = requests.get(url=url)
            req = ob.get_proxy_random(type='socks5')
            return {"proxy_host": req['host'],
                    "proxy_port": req['port']
                    }
        except:
            return {"proxy_host": '103.59.95.71',
                    "proxy_port": '23344'}

    def search(self, query, limit):

        # https://en.wikipedia.org/w/api.php?action=opensearch&search=apple&limit=200
        api_url = self.api_base+'action=opensearch&format=json&search='+query+'&limit='+str(limit)

        response = requests.get(api_url, headers=self.headers, proxies={"http": "socks5://"+self.proxy['proxy_host']+':'+self.proxy['proxy_port']})
        data = json.loads(response.content.decode('utf-8'))
        # print(data)

        if response.status_code == 200:
            k = []
            l = len(data[1])
            if l != 0:
                a, b, c = data[1], data[2], data[3]
                for i in range(l):
                    new_dict = dict()
                    new_dict['title'] = a[i]
                    new_dict['content'] = b[i]
                    if not new_dict['content']:
                        new_dict['content'] = None

                    new_dict['url'] = c[i]
                    new_dict['type'] = 'link'

                    # pol = self.obj.analize_sentiment(b[i])
                    # pol = self.obj.translator(b[i])
                    # new_dict['polarity'] = pol
                    # k.append({'post_title': a[i], 'post_content': b[i], 'post_url': c[i]})
                    k.append(new_dict)

            else:
                k = None

            return k

        else:
            return None

    def processor(self, query, limit):
        OBJ = Wikipedia()
        # print(youtube.searchApi('miller'))
        list_res = OBJ.search(query, limit)
        print(list_res)

        # loop = asyncio.get_event_loop()
        """loop = asyncio.get_event_loop()
           with:
           loop = asyncio.new_event_loop()
           asyncio.set_event_loop(loop)"""

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # print(loop.run_until_complete(OBJ.main(list_res)))
        return loop.run_until_complete(main(list_res))
