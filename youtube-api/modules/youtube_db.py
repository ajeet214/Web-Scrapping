from pymongo import MongoClient
from modules.youtube_api import YoutubeApi, main
from config import Config
import asyncio


class PostSearch:

    def __init__(self):

        self.client = MongoClient(Config.MONGO_URI)
        db = self.client.youtube_db
        self.collection = db.data
        self.dict = {}
        self.obj = YoutubeApi()

    def db_check(self, query):

        r = self.obj.searchApi(query)
        loop = asyncio.get_event_loop()
        s = loop.run_until_complete(main(r))
        # loop.close()
        print(s)
        # print(r)
        t = 0
        for i in r:
            if self.collection.find_one({'url': i['url']}):
                pass
            else:
                # print(i)
                t += 1
                self.collection.insert_one(i)
        self.client.close()
        print('no. of stored pages', t)
        # self.loop.close()

        results = self.db_fetch(query)

        # return {'results': m}
        return {'data': results}

  # ---------------------fetching total number of query pages from database----------------------------------------
    def db_fetch(self, query):
        self.collection.create_index([("title", "text"), ("content", "text")])

        lst = []
        cursor = self.collection.find(
            {"$text": {"$search": query}},
            {'score': {'$meta': "textScore"}}).sort([('score', {'$meta': "textScore"})])
        total = cursor.count()
        n = 0
        for i in cursor:
            # print(i)
            i.pop('_id')
            lst.append(i)
            n += 1

        print('fetched pages from db', len(lst))
        # return {'results': lst,
        #         'total': n}
        return lst


if __name__ == '__main__':
    obj = PostSearch()
    print(obj.db_check("trump"))

# ajeetscbgf@gmail.com
# quality.slip2016@yandex.com
# steve.harvey@list.ru

