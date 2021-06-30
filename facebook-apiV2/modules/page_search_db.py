from modules.fb_private_page_search import PrivatePage
from modules.fb_public_page_search import PageSearch
from pymongo import MongoClient
import asyncio
from config import Config


class Db_processer:

    def __init__(self):

        self.client = MongoClient(Config.DATABASE_CONFIG['host'], Config.DATABASE_CONFIG['port'])
        db = self.client.facebook_db
        self.collection = db.page_search
        self.obj1 = PageSearch()
        self.obj2 = PrivatePage()
        self.loop = asyncio.get_event_loop()

    async def private(self, q):

        self.results2 = self.obj2.fb_pages(q)
        # print(self.results2)
        print('from private search', len(self.results2))

    async def public(self, q):

        await self.private(q)
        self.results1 = self.obj1.fb_page_search(q)
        # print(self.results1)
        print('response from public search', len(self.results1))

    def processor(self, q):

        tasks = [
            asyncio.ensure_future(self.public(q)),
        ]
        self.loop.run_until_complete(asyncio.wait(tasks))

        # print(self.results2)
        for i in self.results2:
            # print(i['page_url'][:-10])
            for t in self.results1:
                # print(t['page_url'])
                # print(t)
                if t['url'] == i['url']:

                    self.results1.remove(t)
        # response from public search results1 after filtering out common pages and from private search results2
        # print(self.results2)
        print('response from public search results1 after filtering out common pages')
        print(self.results1)

        print('pages to be stored')
        m = self.results1+self.results2
        print(m)

        # remaining public pages after filtering out common ones
        d = 0
        for i in self.results1:
            # print(i)
            d += 1
        print('remaining public pages', d)

        # total pages from private search
        c=0
        for i in self.results2:
            # print(i)
            c += 1
        print('total private pages', c)

        # total pages
        e=0
        for i in m:
            # print(i)
            e += 1
        print('total pages to be stored', e)

        # db check
        # if database consists the profile
        t=0
        for i in m:
            if self.collection.find_one({'url': i['url']}):
                pass
            else:
                # print(i)
                t+=1
                self.collection.insert_one(i)
        self.client.close()
        print('no. of stored pages', t)
        # self.loop.close()

        results = self.db_fetch(q)

        # return {'results': m}
        return {'data': results}

    # ---------------------fetching total number of query pages from database----------------------------------------
    def db_fetch(self, query):
        self.collection.create_index([("name", "text"), ("location", "text"), ("description", "text")])

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

    obj = Db_processer()
    # print(obj.processor('elon musk'))
    print(obj.processor('paul smith'))
