from pymongo import MongoClient
from modules.reddit import Reddit
from config import Config


class PostSearch:

    def __init__(self):

        self.client = MongoClient(Config.DATABASE_CONFIG['host'], Config.DATABASE_CONFIG['port'])
        db = self.client.reddit_db
        self.collection = db.data
        self.dict = {}
        self.obj = Reddit()

    def db_check(self, query, post_type):

        response = self.obj.search(query, post_type)
        print(response['data']['results'])
        count = 0
        for i in response['data']['results']:
            if self.collection.find_one({'url': i['url']}):
                pass
            else:
                # print(i)
                count += 1
                self.collection.insert_one(i)
        self.client.close()
        print('no. of stored pages', count)
        # self.loop.close()

        results = self.db_fetch(query)

        # return {'results': m}
        return {'data': results}

    # fetching total number of query pages from database-------------------
    def db_fetch(self, query):
        self.collection.create_index([("title", "text"), ("content", "text")])

        lst = []
        cursor = self.collection.find(
            {"$text": {"$search": query}},
            {'score': {'$meta': "textScore"}}).sort([('score', {'$meta': "textScore"})])
        total = cursor.count()
        count = 0
        for i in cursor:
            # print(i)
            i.pop('_id')
            lst.append(i)
            count += 1

        print('fetched pages from db', len(lst))
        # return {'results': lst,
        #         'total': n}
        return lst


if __name__ == '__main__':
    OBJ = PostSearch()
    print(OBJ.db_check("donald trump", "blog"))

# ajeetscbgf@gmail.com
# quality.slip2016@yandex.com
# steve.harvey@list.ru
