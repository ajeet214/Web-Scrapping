from urllib.parse import urlencode
from bs4 import BeautifulSoup
from time import sleep
import demjson
import redis
import multiprocessing
import json
from config import Config
from modules import login_file
from modules import minio_push


class GroupSearch:

    def __init__(self):

        # self.redis_host = Config.REDIS_CONFIG['host']
        # self.redis_port = Config.REDIS_CONFIG['port']

        login = login_file.Login()
        login.loginmethod()
        self.client = login.client
        # self.name = name

    # -----------------------------------------------------------------------------
    def redis_channel(self, session_id):

        # r = redis.Redis(host=self.redis_host, port=self.redis_port)
        r = redis.from_url("redis://"+Config.REDIS_URI)
        client_id = 'linkedin_group_search' + session_id
        p = r.pubsub()  # pubsub object
        p.subscribe(client_id)
        return client_id, r, p

    def _dicteditor(self, data, client_id, redis_obj, channel_obj):

        soup = BeautifulSoup(data, 'lxml')
        # print(soup)
        data = demjson.decode([each_code.text for each_code in soup.find_all('code')][-3])

        total_res = data['data']['metadata']['totalResultCount']
        # print(total_res)
        temp_lst2 = []

        data1 = data['data']['elements']
        # print(data1[0]['elements'])
        for i in data1:
            try:
                if len(i['elements']) == 0:
                    pass
                else:
                    # print(len(i['elements']))
                    for j in i['elements']:
                        temp_dct2 = dict()
                        temp_dct2['group_members'] = j['headline']['text'].replace(
                            ' members', '').replace(' member', '').replace(',', '')
                        temp_dct2['trackingUrn'] = j['trackingUrn']
                        temp_lst2.append(temp_dct2)
            except KeyError:
                pass
        # print(temp_lst2)
        # -------------------------------
        data2 = data['included']
        # print(data2)

        temp_lst1 = []
        for i in data2:
            temp_dct = dict()
            temp_dct['name'] = i['groupName']
            temp_dct['description'] = i['groupDescription']
            temp_dct['objectUrn'] = i['objectUrn']
            temp_dct['url'] = "https://www.linkedin.com/"+i['objectUrn'].replace('urn:li:group:', 'groups/')
            temp_dct['type'] = 'group'

            # try:
            #     temp_dct['image'] = i['logo']['rootUrl']+i['logo']['artifacts'][1]['fileIdentifyingUrlPathSegment']
            # except:
            #     temp_dct['image'] = None

            try:
                image_url = i['logo']['rootUrl']+i['logo']['artifacts'][1]['fileIdentifyingUrlPathSegment']
                minio_url = minio_push.start_uploading([image_url], 'linkedin-service')
                for i in minio_url:
                    if i['status'] == 200:
                        temp_dct['image'] = i['file_url']
                    else:
                        raise Exception('image not found')
            except:
                temp_dct['image'] = None

            temp_lst1.append(temp_dct)

        # print(temp_lst1)

        #---------------------------------
        for x in temp_lst1:
            for y in temp_lst2:

                if y['trackingUrn'] == x['objectUrn']:
                    x['group_members'] = int(y['group_members'].replace('Group â\x80¢ ', ''))

            x.pop('objectUrn')
            print(x)
            redis_obj.publish(client_id, json.dumps(x))

        return temp_lst1, total_res

    def pagination(self, first_page_url, client_id, redis_obj, channel_obj):

        condition = True
        page_number = 1
        c = 1

        while condition:

            if page_number == 1:
                k = self.client.get(first_page_url)
            else:
                k = self.client.get(first_page_url+"&page={}".format(page_number))
            # print(k.text)
            result, total = self._dicteditor(k.text, client_id, redis_obj, channel_obj)

            page_number += 1
            
            number_of_total_pages = int(total/10)

            # print(number_of_total_pages)
            if number_of_total_pages < 20:

                if number_of_total_pages <= 1:
                    condition = False
                    redis_obj.publish(client_id, 'EOF')
                    channel_obj.unsubscribe(client_id)
                pass
            if c == 20:
                condition = False
                redis_obj.publish(client_id, 'EOF')
                channel_obj.unsubscribe(client_id)
            c += 1
            sleep(1)

            # next_page_url = first_page_url+'&page={}'
            # count = 2
            # contdition = True
            # while contdition:
            #     if count == 3:
            #         contdition = False
            #     else:
            #         url = next_page_url.format(count)
            #         print(url)
            #         k = self.client.get(url)
            #         res, t = self._dicteditor(k.text)
            #     count += 1

# ----------------------------------------------------------------

    def search(self, name):

        urlpart = urlencode(
            {"keywords": name, "origin": "GLOBAL_SEARCH_HEADER"}
        )
        first_page_url = "https://www.linkedin.com/search/results/groups/?" + urlpart

        print(first_page_url)
        k = self.client.get(first_page_url)
        # print(k)
        # print(k.text)
        # print(self._dicteditor(k.text))
        soup1 = BeautifulSoup(k.text, 'lxml')

        data = demjson.decode([each_code.text for each_code in soup1.find_all('code')][-3])
        total_res = data['data']['metadata']['totalResultCount']
        print(total_res)
        if total_res == 0:
            return {"message": "no data found"}

        # print(str(self.client).replace('<requests.sessions.Session object at ', ''))

        session_id = str(self.client).replace('<requests.sessions.Session object at ', '')
        client_id, redis_obj, channel_obj = self.redis_channel(session_id)
        t = multiprocessing.Process(target=self.pagination,
                                    args=(first_page_url, client_id, redis_obj, channel_obj))
        t.start()

        return {"channel_id": client_id}


if __name__ == '__main__':
    obj = GroupSearch()
    # print(obj.search('team'))
    # print(obj.search('markel'))
    print(obj.search('tamer'))
