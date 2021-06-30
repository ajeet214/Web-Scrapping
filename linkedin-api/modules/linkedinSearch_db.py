from pymongo import MongoClient
from modules.linkedinSearch import SearchClass
from config import Config


class LinkedinSearch:

    def __init__(self):

        self.client = MongoClient(Config.MONGO_URI)
        db = self.client.linkedin_db
        self.collection = db.search
        self.dict = {}
        self.obj = SearchClass()

    def db_check(self, query):

        r = self.obj.search(query)
        print(r)
        t = 0
        for i in r['results']:
            if self.collection.find_one({'userid': i['userid']}):
                pass
            else:
                # print(i)
                t += 1
                self.collection.insert_one(i)
        self.client.close()
        print('no. of stored pages', t)
        # self.loop.close()

        results = self.db_fetch(query)
        #
        # # return {'results': m}
        return {'data': results}

  # ---------------------fetching total number of query pages from database----------------------------------------
    def db_fetch(self, query):
        self.collection.create_index([("name", "text")])

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
    obj = LinkedinSearch()
    print(obj.db_check("mark"))

