from pymongo import MongoClient
from modules.Id_checker import LinkedinId
from config import Config


class ProfileExistence:

    def __init__(self):

        self.client = MongoClient(Config.MONGO_URI)
        db = self.client.linkedin_db
        self.collection = db.data
        self.dict = dict()

    def db_check(self, number):

        # for i in self.collection.find({'num'}):
        #     pprint.pprint(i['num'])

        # if database consists the profile
        if self.collection.find_one({'profile': number}):

            for doc in self.collection.find({'profile':  number}):
                # print(doc)
                self.dict['profileExists'] = doc['profileExists']
                self.dict['profile'] = doc['profile']

                return self.dict

        # when profile isn't in database
        else:
            obj = LinkedinId()
            data_from_fb = obj.id_check(number)
            # print(data_from_fb)
            self.db_loader(data_from_fb)
            return data_from_fb

    def db_loader(self, data):

        # print(data)
        if data['profileExists'] is False:
            pass
        else:

            d = {"profileExists": data['profileExists'],
                 "profile": data['profile']
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
    print(obj.db_check("ajeetscbgf@gmail.com"))

# ajeetscbgf@gmail.com
# quality.slip2016@yandex.com
# steve.harvey@list.ru