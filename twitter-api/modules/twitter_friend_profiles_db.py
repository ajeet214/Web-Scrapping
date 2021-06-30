from modules.twitterprofile import ProfileClass
from pymongo import MongoClient
from config import Config


class FriendsProfileFetch:

    def __init__(self):

        self.client = MongoClient(Config.MONGO_URI)
        db = self.client.twitter_db
        self.collection = db.profile_fetch
        self.obj1 = ProfileClass()

    def fetcher(self, q, limit=None):

        result = self.obj1.friendsprofile(q, limit)
        self.db_check(result)
        # print(result)
        res = []
        for i in result:
            # print(i['entities'])

            urls_list = []
            try:
                # print(i['entities']['url']['urls'])
                i['entities']['url']['urls'][0].pop('indices')
                i['entities']['url']['urls'][0].pop('display_url')
                # print(i['entities']['url']['urls'])

                urls_list.append(i['entities']['url']['urls'][0]['url'])
                urls_list.append(i['entities']['url']['urls'][0]['expanded_url'])

            except KeyError:
                pass
            try:
                # print(doc['entities']['description']['urls'])
                if len(i['entities']['description']['urls']) != 0:

                    # print(doc['entities']['description']['urls'][0]['expanded_url'])
                    # print(i['entities']['description']['urls'])
                    i['entities']['description']['urls'][0].pop('indices')
                    i['entities']['description']['urls'][0].pop('display_url')
                    # print(i['entities']['description']['urls'])

                    urls_list.append(i['entities']['description']['urls'][0]['url'])
                    urls_list.append(i['entities']['description']['urls'][0]['expanded_url'])
                else:
                    pass
            except KeyError:
                pass
            i.pop('entities')
            # print(urls_list)
            i['linked_urls'] = urls_list
            res.append(i)

        return {'data': {'results': res}}

    def db_check(self, r):

        for each_friend in r:
            # print(each_friend['profile_url'])

            # if database consists the profile
            if self.collection.find_one({'profile_url': each_friend['profile_url']}):

                for doc in self.collection.find({'profile_url': each_friend['profile_url']}):
                    pass
                    # print(doc)


            # when profile isn't in database
            else:
                self.collection.insert_one(each_friend)

                # close db connection
                self.client.close()


if __name__ == '__main__':
    obj = FriendsProfileFetch()
    print(obj.fetcher("realdonaldtrump"))

