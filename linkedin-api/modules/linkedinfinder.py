from urllib.parse import urlencode
import pymongo
from bs4 import BeautifulSoup
import demjson
# config file
from config import Config
from modules import login_file


class SearchClass:

    def __init__(self, name):

        self.lst = []
        self.temp_lst1 = []
        self.lst1 = []
        self.temp_lst2 = []
        mon = pymongo.MongoClient(Config.MONGO_URI)
        db = mon[login_file.db]
        self.collection = db[login_file.collection_search]
        urlpart = urlencode(
            {"keywords": name, "origin": "GLOBAL_SEARCH_HEADER"}
        )

        self.url = "https://www.linkedin.com/search/results/people/?"+urlpart
        login = login_file.Login()
        login.loginmethod()
        self.client = login.client
        self.name = name

    # def _urlHandler(self, page):
    #     url = self.url +"&page="+str(page)
    #     return url

    # def _insertfunction(self, data):
    #     try:
    #         records = self.collection.find({"publicIdentifier": data["publicIdentifier"]})
    #         if records.count() == 0:
    #             self.collection.insert(data)
    #     except:
    #         print("error>>insetfunction::", sys.exc_info()[1])
    # -----------------------------------------------------------------------------

    def _dicteditor(self, data):

        soup = BeautifulSoup(data, 'html.parser')
        # print(soup)
        for each_code in soup.find_all('code'):
            # lst.append(each_code.text)
            self.lst.append(each_code.text)
        # print(self.lst[-3])
        data = demjson.decode(self.lst[-3])
        # print(data)
        data1 = data['data']['elements']
        # print(data1)
        for i in data1:
            try:
                if len(i['elements']) == 0:
                    pass
                else:
                    # print(len(i['elements']))
                    for j in i['elements']:
                        temp_dct2 = {}
                        temp_dct2['location'] = j['subline']['text']
                        temp_dct2['userid'] = j['publicIdentifier']
                        temp_dct2['full_name'] = j['title']['text']
                        self.temp_lst2.append(temp_dct2)
            except KeyError:
                pass

        # print(self.temp_lst2)
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

        # print(self.lst1)
        for i in self.lst1:
            temp_dct = {}
            temp_dct['firstName'] = i['firstName']
            temp_dct['lastName'] = i['lastName']
            temp_dct['userid'] = i['publicIdentifier']
            temp_dct['type'] = 'identity'
            temp_dct['url'] = "https://www.linkedin.com/in/"+i['publicIdentifier']
            try:
                temp_dct['occupation'] = i['occupation']
            except:
                pass
            try:
                temp_dct['image'] = i['picture']['rootUrl']+i['picture']['artifacts'][-1]['fileIdentifyingUrlPathSegment']
            except:
                pass

            self.temp_lst1.append(temp_dct)
        # print(self.temp_lst1)

        #---------------------------------
        for x in self.temp_lst1:
            for y in self.temp_lst2:

                if y['userid'] == x['userid']:
                    x['location'] = y['location']
                    x['full_name'] = y['full_name']



        return self.temp_lst1

# ----------------------------------------------------------------
    def search(self):


        print(self.url)
        k = self.client.get(self.url)
        # print(k)
        # print(k.text)
        return self._dicteditor(k.text)


def profilesearch(name):

    searchprofile = SearchClass(name=name)
    return searchprofile.search()



if __name__ == '__main__':
    print(profilesearch("steve"))

# Juha Sipilä
# Владимир Путин
# Nguyễn Xuân Phúc