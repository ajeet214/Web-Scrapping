from modules.linkedinprofile import ProfileFetcher
from pymongo import MongoClient
from config import Config


class ProfileFetch:

    def __init__(self):

        self.client = MongoClient(Config.MONGO_URI)
        db = self.client.linkedin_db
        self.collection = db.profile_fetch
        self.obj1 = ProfileFetcher()

    def fetcher(self, q):

        result = self.obj1.Porfile(q)
        # print(result)
        return result

    def db_check(self, r):

        # print(r['profile_url'])
        # if database consists the profile
        if self.collection.find_one({'profile_url': 'https://www.linkedin.com/in/' + r}):

            for doc in self.collection.find({'profile_url': 'https://www.linkedin.com/in/' + r}):
                # print(doc)
                doc.pop('_id')
                # self.dict['profileExists'] = doc['profileExists']
                # self.dict['profile_id/num'] = doc['profile_id/num']
                #
                return {'data': doc}

        # when profile isn't in database
        else:
            data_from_linkedin = self.fetcher(r)
            # print(data_from_fb)
            self.db_loader(data_from_linkedin)
            data_from_linkedin.pop('_id')

            return {'data': data_from_linkedin}

    def db_loader(self, data):

        # print(data)
        self.collection.insert_one(data)

        # close db connection
        self.client.close()


if __name__ == '__main__':
    obj = ProfileFetch()
    print(obj.db_check("firdausbhathena"))

# priscilla
# hasan.ustun.3762
# 100000143127056
# senol.oezdemir1