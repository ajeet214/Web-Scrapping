import sys
from modules.woeid_finder import WOEID
import tweepy
from modules.caps_client import CapsClient


class GeoTrend:

    def __init__(self):

        self.client = WOEID()
        cred = CapsClient().get_credential_random('twitter')['api_key']

        try:
            self.auth = tweepy.OAuthHandler(cred['consumer_key'], cred['consumer_secret'])
            self.auth.set_access_token(cred['access_token'], cred['access_token_secret'])
            self.api = tweepy.API(self.auth)
        except:
            print("error::init>>", sys.exc_info()[1])

    def _woeid_id_finder(self, area_name):

        try:
            return self.client.fetch_woeid(area_name)
        except:
            print("error::woeid_id_finder>>", sys.exc_info()[1])
        # try:
        #     import os
        #     dir_path = os.path.dirname(os.path.realpath(__file__))
        #     with open(dir_path+"/woeid.json", "r") as f :
        #         jsondata = f.read()
        #     # this will return "woeid" id on the baise of countryCode
        #     woeiddata = json.loads(jsondata)
        #     for i in woeiddata:
        #         if (i["name"].lower() == area_name.lower()):
        #             return i["woeid"]
        #     return "Worng_Code"
        # except:
        #     print("error::woeid_id_finder>>", sys.exc_info()[1])

    def geoStream(self, area_name):
        try:
            if area_name:
                woeid = self._woeid_id_finder(area_name=area_name)
                print(woeid)
                trends1 = self.api.trends_place(woeid)
            else:
                trends1 = self.api.trends_place(1)
            data = trends1[0]
            return {'data': data['trends']}

        except:
            print("error::geoStream>>", sys.exc_info()[1])
            return "error"

    def __del__(self):
        try:
            pass
        except:
            print("error::del>>", sys.exc_info()[1])


if __name__ == '__main__':
    obj = GeoTrend()
    print(obj.geoStream(area_name="london"))
