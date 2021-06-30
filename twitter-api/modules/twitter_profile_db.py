from modules.twitterprofile import ProfileClass
from pymongo import MongoClient
from config import Config


class ProfileFetch:

    def __init__(self):

        self.client = MongoClient(Config.MONGO_URI)
        db = self.client.twitter_db
        self.collection = db.profile_fetch
        self.obj1 = ProfileClass()

    def fetcher(self, q):

        result = self.obj1.profilefetcher(q)
        # print(result)
        return result

    def db_check(self, r):

        r = r.lower()
        # if database consists the profile
        if self.collection.find_one({'profile_url': 'https://twitter.com/' + r}):

            for doc in self.collection.find({'profile_url': 'https://twitter.com/' + r}):
                # print(doc)
                doc.pop('_id')
                # self.dict['profileExists'] = doc['profileExists']
                # self.dict['profile_id/num'] = doc['profile_id/num']
                urls_list = []

                try:
                    # print(doc['entities']['url']['urls'])
                    doc['entities']['url']['urls'][0].pop('indices')
                    doc['entities']['url']['urls'][0].pop('display_url')

                    urls_list.append(doc['entities']['url']['urls'][0]['url'])
                    urls_list.append(doc['entities']['url']['urls'][0]['expanded_url'])

                except KeyError:
                    pass
                try:
                    # print(doc['entities']['description']['urls'])
                    if len(doc['entities']['description']['urls']) != 0:

                        # print(doc['entities']['description']['urls'][0]['expanded_url'])
                        # print(doc['entities']['description']['urls'])
                        doc['entities']['description']['urls'][0].pop('indices')
                        doc['entities']['description']['urls'][0].pop('display_url')

                        urls_list.append(doc['entities']['description']['urls'][0]['url'])
                        urls_list.append(doc['entities']['description']['urls'][0]['expanded_url'])
                    else:
                        pass
                except KeyError:
                    pass
                doc.pop('entities')
                # print(urls_list)
                doc['linked_urls'] = urls_list
                # print(doc['entities']['url']['urls'])
                # doc['entities']['url']['urls']
                return {'data': doc}

        # when profile isn't in database
        else:
            # try:
            data_from_fb = self.fetcher(r)
            # print(data_from_fb)
            self.db_loader(data_from_fb)
            data_from_fb.pop('_id')
            urls_list = []
            try:
                # print(data_from_fb['entities']['url']['urls'])
                data_from_fb['entities']['url']['urls'][0].pop('indices')
                data_from_fb['entities']['url']['urls'][0].pop('display_url')

                urls_list.append(data_from_fb['entities']['url']['urls'][0]['url'])
                urls_list.append(data_from_fb['entities']['url']['urls'][0]['expanded_url'])

            except KeyError:
                pass
            try:
                # print(doc['entities']['description']['urls'])
                if len(data_from_fb['entities']['description']['urls']) != 0:

                    # print(doc['entities']['description']['urls'][0]['expanded_url'])
                    # print(data_from_fb['entities']['description']['urls'])
                    data_from_fb['entities']['description']['urls'][0].pop('indices')
                    data_from_fb['entities']['description']['urls'][0].pop('display_url')

                    urls_list.append(data_from_fb['entities']['description']['urls'][0]['url'])
                    urls_list.append(data_from_fb['entities']['description']['urls'][0]['expanded_url'])
                else:
                    pass
            except KeyError:
                pass
            data_from_fb.pop('entities')
            # print(urls_list)
            data_from_fb['linked_urls'] = urls_list
            return {'data': data_from_fb}

    def db_loader(self, data):

        # print(data)
        self.collection.insert_one(data)

        # close db connection
        self.client.close()


if __name__ == '__main__':
    obj = ProfileFetch()
    print(obj.db_check("tuckercarlson"))

