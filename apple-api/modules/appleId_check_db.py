from pymongo import MongoClient
from modules.appleId_check import AppleId
from config import Config


class ProfileExistence:

    def __init__(self):

        self.client = MongoClient(Config.MONGO_URI)
        db = self.client.Apple_db
        self.collection = db.account
        self.dict = {}

    def db_check(self, id):

        # if database consists the profile
        if self.collection.find_one({'profile_id': id}):

            for doc in self.collection.find({'profile_id': id}):
                # print(doc)
                self.dict['profileExists'] = doc['profileExists']
                self.dict['profile_id'] = doc['profile_id']

                return self.dict

        # when profile isn't in database
        else:
            obj = AppleId()
            data_from_apple = obj.id_check(id)
            # print(data_from_fb)
            self.db_loader(data_from_apple)
            return data_from_apple

    def db_loader(self, data):

        # print(data)
        if data['profileExists'] is False:
            pass
        else:

            d = {"profileExists": data['profileExists'],
                 "profile_id": data['profile_id']
                 }
            self.collection.insert_one(d)

            # close db connection
            self.client.close()


if __name__ == '__main__':
    obj = ProfileExistence()
    print(obj.db_check("jaqsoms43@gmail.com"))

