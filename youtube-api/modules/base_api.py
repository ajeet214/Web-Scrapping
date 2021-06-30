# from core.db.mongodb import Mongo_db_store
import requests
import json
# from bson import json_util

class BaseApi:
    def __init__(self, username=None, password=None, auth_token=None, auth_secret = None, social=None):
        if social is None:
            raise Exception('Social value not provided')
        self.username = username
        self.password = password
        self.auth_token = auth_token
        self.auth_secret = auth_secret
        self.proxy = self._get_proxy()

    def _get_proxy(self):

        url = "http://credsnproxy/api/v1/proxy"
        try:
            creds = requests.get(url=url).json()

        except:
            return {"proxy_host": '5.39.20.153',
                    "proxy_port": '25567'}

    def get_request(self, url,getStatus = False):
        headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0'}
        print(str(self.__class__) +" Requesting Url: "  + url)
        if getStatus:
            return requests.get(url=url, headers=headers, proxies={"http": "//socks5://"+self.proxy['proxy_host']+':'+self.proxy['proxy_port']}).content,
        else:
            return requests.get(url=url, headers=headers, proxies={"http": "//socks5://"+self.proxy['proxy_host']+':'+self.proxy['proxy_port']}).content


    def post_request(self,url,data):
        return requests.post(url=url,data=data).content

    def save_data(self,collectionname , data):
        if collectionname is None:
            raise Exception('Collection name cannot be empty')
        if data is None:
            raise Exception("Data cannot be empty")
        mongo = Mongo_db_store(collectionname=collectionname)
        mongo.setdata(data=data)


    def search(self, query, stype=None):
         data = self.searchApi(query=query, stype=stype)
         return self.toJson(data)

    # def toJson(self, data):
    #     return json.dumps(data, default=json_util.default)

    def searchApi(self, query, stype=None):
        raise Exception('Not implemented search data base_api')

    def getInfo(self):
        pass

    def getTree(self):
        pass

    def getrelativeActors(self):
        """
        return relative actors of particular network
        """
        pass