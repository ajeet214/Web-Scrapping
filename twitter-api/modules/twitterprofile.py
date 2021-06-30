import sys
# from modules.sentiment import Sentiment_analysis
import tweepy
from credentials import TwitterKeys
import time
# temp lib


class ProfileClass:

    def __init__(self):

        # self.neg_count = 0
        # self.neu_count = 0
        # self.pos_count = 0
        # self.obj = Sentiment_analysis()
        cred = TwitterKeys()
        try:
            self.auth = tweepy.OAuthHandler(cred.consumer_key, cred.consumer_secret)
            self.auth.set_access_token(cred.access_token, cred.access_token_secret)
            self.api = tweepy.API(self.auth)
        except:
            print("error>>init::", sys.exc_info()[1])

    def _objecttodict(self, profileobj):
        temp = dict()

        # print(profileobj)

        temp["profile_created_at"] = profileobj.created_at.strftime('%m/%d/%Y %H:%M:%S')
        temp["profile_created_at"] = int(time.mktime(time.strptime(temp["profile_created_at"], '%m/%d/%Y %H:%M:%S'))) - time.timezone

        temp["description"] = profileobj.description
        if not temp["description"]:
            temp["description"] = None

        # pol = self.obj.analize_sentiment(profileobj.description)
        # temp['polarity'] = pol
        #
        # if pol == 1:
        #     temp['polarity'] = 'positive'
        #     self.pos_count += 1
        # elif pol == -1:
        #     temp['polarity'] = 'negative'
        #     self.neg_count += 1
        # else:
        #     temp['polarity'] = 'neutral'
        #     self.neu_count += 1

        temp["verified"] = profileobj.verified

        if profileobj.entities is not None:
            temp["entities"] = profileobj.entities

        temp["favourites_count"] = profileobj.favourites_count
        temp["followers_count"] = profileobj.followers_count
        temp["friends_count"] = profileobj.friends_count
        k = str(profileobj.location)
        if k == "":
            temp["location"] = None
        else:
            temp["location"] = profileobj.location
        temp["name"] = profileobj.name
        temp["profile_image_url"] = profileobj.profile_image_url_https
        temp["screen_name"] = profileobj.screen_name
        temp["statuses_count"] = profileobj.statuses_count
        temp["profile_url"] = 'https://twitter.com/'+profileobj.screen_name.lower()
        try:
            temp["profile_banner_url"] = profileobj.profile_banner_url
        except:
            temp["profile_banner_url"] = None

        temp['type'] = 'identity'

        return temp

    def profilefetcher(self, name):
        try:
            response = self.api.get_user(name)
            k = self._objecttodict(response)
            # self.collection.insert(k.copy())
            # if k == None:
            #     raise Exception
            # return {'results': k}
            return k

        except TypeError:
            return sys.exc_info()[1]
            # print("error>>profilefetcher::", sys.exc_info()[1])


if __name__ == '__main__':
    tmp = ProfileClass()
    print((tmp.profilefetcher("realdonaldtrump")))

