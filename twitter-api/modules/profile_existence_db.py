from pymongo import MongoClient
from modules.Id_checker import EmailChecker
from config import Config


class ProfileExistence:

    def __init__(self):

        self.client = MongoClient(Config.MONGO_URI)
        db = self.client.twitter_db
        self.collection = db.data
        self.dict = {}

    def db_check(self, number):

        # for i in self.collection.find({'num'}):
        #     pprint.pprint(i['num'])

        # if database consists the profile
        if self.collection.find_one({'contacts': number}):

            for doc in self.collection.find({'contacts': number}):
                # print(doc)
                self.dict['profileExists'] = doc['profileExists']
                self.dict['contacts'] = doc['contacts']

                return self.dict

        # when profile isn't in database
        else:
            obj = EmailChecker()
            data_from_fb = obj.checker(number)
            # print(data_from_fb)
            self.db_loader(data_from_fb)
            return data_from_fb

    def db_loader(self, data):

        # print(data)
        if data['profileExists'] is False:
            pass
        else:

            d = {"profileExists": data['profileExists'],
                 "contacts": data['contacts']
                 }
            self.collection.insert_one(d)

            # close db connection
            self.client.close()

    # pprint.pprint(self.collection.find({'num'}))
    # else:
    #     print('**')
    #     print(self.obj.caller_data(number))

    # print(self.collection.count())
    # pprint.pprint(collection.find_one({}))
    # for i in self.collection.find():
    #     # pprint.pprint(i['num'])
    #     if number == i['num']:
    #         print(i['num'])
    #         return i['result']
    #     else:
    #         return self.obj.caller_data(number)


if __name__ == '__main__':
    obj = ProfileExistence()
    print(obj.db_check("919717896555"))
    # print(obj.db_check("justinmat1994@outlook.com"))
# +97433013503
