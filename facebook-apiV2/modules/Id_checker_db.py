from pymongo import MongoClient
from modules.Id_checker import EmailNumberChecker
from config import Config


class Profile_existance:

    def __init__(self):

        self.client = MongoClient(Config.DATABASE_CONFIG['host'], Config.DATABASE_CONFIG['port'])
        db = self.client.facebook_db
        self.collection = db.data
        self.dict = {}

    def db_check(self, number):

        # for i in self.collection.find({'num'}):
        #     pprint.pprint(i['num'])

        # if database consists the profile
        if self.collection.find_one({'profile_id/num': number}):

            for doc in self.collection.find({'profile_id/num':  number}):
                # print(doc)
                self.dict['profileExists'] = doc['profileExists']
                self.dict['profile_id/num'] = doc['profile_id/num']

                return self.dict

        # when profile isn't in database
        else:
            obj = EmailNumberChecker()
            data_from_fb = obj.Checker(number)
            # print(data_from_fb)
            self.db_loader(data_from_fb)
            return data_from_fb

    def db_loader(self, data):

        # print(data)
        if data['profileExists'] is False:
            pass
        else:

            d = {"profileExists": data['profileExists'],
                 "profile_id/num": data['profile_id/num']
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
    obj = Profile_existance()
    print(obj.db_check("917726933456"))
# +97433013503
