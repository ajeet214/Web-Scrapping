# from modules.profile_fetch import ProfileFetch
from modules.profile_fetcher2 import ProfileFetch
from pymongo import MongoClient
from config import Config


class ProfileFetchDb:

    def __init__(self):

        self.client = MongoClient(Config.DATABASE_CONFIG['host'], Config.DATABASE_CONFIG['port'])
        db = self.client.facebook_db
        self.collection = db.profile_fetch

    def fetcher(self, q):

        obj1 = ProfileFetch()
        result = obj1.fb_profile_fetch(q)
        # print(result)
        return result

    def db_check(self, r):

        # print(r['profile_url'])
        # if database consists the profile
        if self.collection.find_one({'profile_url': 'https://www.facebook.com/'+r}):

            for doc in self.collection.find({'profile_url':  'https://www.facebook.com/'+r}):
                # print(doc)
                doc.pop('_id')
                # self.dict['profileExists'] = doc['profileExists']
                # self.dict['profile_id/num'] = doc['profile_id/num']
                #
                return {'data': doc}

        # when profile isn't in database
        else:
            data_from_fb = self.fetcher(r)
            # print(data_from_fb)
            self.db_loader(data_from_fb)
            data_from_fb.pop('_id')

            return {'data': data_from_fb}

    def db_loader(self, data):

        # print(data)
        self.collection.insert_one(data)

        # close db connection
        self.client.close()


if __name__ == '__main__':
    obj = ProfileFetchDb()
    print(obj.db_check("ickinekin"))

# priscilla
# hasan.ustun.3762
# 100000143127056
# senol.oezdemir1