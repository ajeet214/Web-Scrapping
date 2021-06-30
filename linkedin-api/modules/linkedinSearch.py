from urllib.parse import urlencode
import pymongo
from bs4 import BeautifulSoup
import demjson
# config file
from requests_futures.sessions import FuturesSession
from concurrent.futures import ThreadPoolExecutor
from credentials import creds

from modules import login_file


class SearchClass:

    def __init__(self):
        self.session = FuturesSession(executor=ThreadPoolExecutor(max_workers=5))

        self.lst = []
        self.temp_lst1 = []
        self.lst1 = []
        self.temp_lst2 = []
        self.location_list = []
        mon = pymongo.MongoClient(host=login_file.host, port=login_file.port)
        db = mon[login_file.db]
        self.collection = db[login_file.collection_search]

    # -----------------------------------------------------------------------------

    def _dicteditor(self, data):
        data = data.encode('latin1').decode('utf8')
        # print(data)
        soup = BeautifulSoup(data, 'html.parser')
        # print(soup)
        for each_code in soup.find_all('code'):
            # lst.append(each_code.text)
            self.lst.append(each_code.text)
        # print(self.lst[-3])
        data = demjson.decode(self.lst[-3])
        print(data)
        data1 = data['data']['elements']
        print('data1', data1)

        for i in data1:

            if i['type'] == 'SEARCH_HITS':

                for j in i['elements']:
                    temp_dct2 = dict()

                    # for non linkedin members
                    try:
                        temp_dct2['userid'] = j['publicIdentifier']
                        temp_dct2['location'] = j['subline']['text']
                        temp_dct2['full_name'] = j['title']['text']
                        self.temp_lst2.append(temp_dct2)

                    # if linkedin member then pass
                    except KeyError:
                        pass
            else:
                pass
            # try:
            #     if len(i['elements']) == 0:
            #         pass
            #     else:
            #         # print(len(i['elements']))
            #         for j in i['elements']:
            #             temp_dct2 = {}
            #             temp_dct2['location'] = j['subline']['text']
            #             temp_dct2['userid'] = j['publicIdentifier']
            #             temp_dct2['full_name'] = j['title']['text']
            #             self.temp_lst2.append(temp_dct2)
            # except KeyError:
            #     pass

        print('fullname,location,userid\n', self.temp_lst2)
        data2 = data['included']
        # print(data2)
        # print(demjson.encode(data2))

        # ---------------------------------
        for dct in data2:
            # print(dct,'\n')
            if "firstName" in dct:
                if dct['firstName'] == "":
                    pass
                # print(dct['entityUrn'][22:])
                else:
                    self.lst1.append(dct)

        # print('firstname,lastname ...\n', self.lst1)
        for i in self.lst1:
            temp_dct = {}
            # temp_dct['firstName'] = i['firstName']
            # temp_dct['lastName'] = i['lastName']
            temp_dct['userid'] = i['publicIdentifier']
            temp_dct['url'] = "https://www.linkedin.com/in/"+i['publicIdentifier']
            try:
                temp_dct['description'] = i['occupation']
            except:
                pass
            try:
                temp_dct['image'] = i['picture']['rootUrl']+i['picture']['artifacts'][-1]['fileIdentifyingUrlPathSegment']
            except:
                temp_dct['image'] = None

            self.temp_lst1.append(temp_dct)
        print("url,userid,image&des\n", self.temp_lst1)


        #---------------------------------
        for x in self.temp_lst1:
            for y in self.temp_lst2:

                if y['userid'] == x['userid']:
                    x['location'] = y['location']
                    self.location_list.append(x['location'])
                    x['name'] = y['full_name']


        print('locations\n', self.location_list)


        rs = []
        for u in self.location_list:
            rs.append(self.session.get('https://maps.google.com/maps/api/geocode/json?address=' + str(
                u) + '&key='+creds['google_key']))
        results = []
        for response in rs:
            temp_dict = {}
            r = response.result()
            lt = demjson.decode(r.content.decode('utf-8'))
            # print(lt)
            # print(lt['results'][0]['address_components'])
            try:
                for i in lt['results'][0]['address_components']:
                    if i['types'][0] == 'country':
                        # print(i['long_name'])
                        temp_dict['country_code'] = i['short_name']
                        temp_dict['country'] = i['long_name']
                        results.append(temp_dict)
            except:
                temp_dict['country_code'] = None
                temp_dict['country'] = None
                results.append(temp_dict)
        #
        print(results)
        print(self.temp_lst1)
        final_list = []
        for i in range(len(self.temp_lst1)):
            final_dict = {}
            try:
                final_dict['location'] = self.temp_lst1[i]['location']
            except:
                final_dict['location'] = None

            if self.temp_lst1[i]['location'] is None:
                final_dict['country_code'] = None
                final_dict['country'] = None
            else:
                final_dict['country_code'] = results[i]['country_code']
                final_dict['country'] = results[i]['country']

            final_dict['url'] = self.temp_lst1[i]['url']
            final_dict['userid'] = self.temp_lst1[i]['userid']

            try:
                final_dict['image'] = self.temp_lst1[i]['image']
            except:
                final_dict['image'] = None

            final_dict['name'] = self.temp_lst1[i]['name']
            final_dict['description'] = self.temp_lst1[i]['description']
            # type is by default identity
            final_dict['type'] = 'identity'
            final_list.append(final_dict)
        return final_list


        # return self.temp_lst1

# ----------------------------------------------------------------
    def search(self, name):

        urlpart = urlencode(
            {"keywords": name, "origin": "GLOBAL_SEARCH_HEADER"}
        )

        self.url = "https://www.linkedin.com/search/results/people/?" + urlpart
        login = login_file.Login()
        login.loginmethod()
        self.client = login.client
        self.name = name

        # print(self.url)
        k = self.client.get(self.url)
        # print(k)
        # print(k.text)
        res = self._dicteditor(k.text)
        return {"results": res}


if __name__ == '__main__':

    obj = SearchClass()
    print(obj.search("Juha Sipilä"))

# Juha Sipilä
# Владимир Путин
# Nguyễn Xuân Phúc