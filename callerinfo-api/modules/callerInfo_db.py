from pymongo import MongoClient
from modules.caller_info_twilio import NumberInfo
from modules.data_gathering import DataSheet
from config import Config


class CallerInfo:

    def __init__(self):

        self.client = MongoClient(Config.DATABASE_CONFIG['host'], Config.DATABASE_CONFIG['port'])
        db = self.client.caller_info_db
        self.collection = db.data
        self.obj = NumberInfo()
        self.dict = {}
        self.obj2 = DataSheet()

    def db_check(self, number):

        # print(number)

        # for i in self.collection.find({'num'}):
        #     pprint.pprint(i['num'])

        # when number is already in db
        if self.collection.find_one({'number': '+'+ number}):
            for doc in self.collection.find({'number': '+'+ number}):
                # print(doc)
                doc.pop('_id')

                # print(doc['result'])
                # print(doc['result']['data'][0])
                # print(doc['result']['data'][0]['name'])
                self.dict['carrier_name'] = doc['carrier_name']
                # print(doc['result']['data'][0]['score'])
                self.dict['mobile_network_code'] = doc['mobile_network_code']
                self.dict['country_code'] = doc['country_code']

                # print(doc['result']['data'][0]['phones'])
                self.dict['number_type'] = doc['number_type']
                self.dict['mobile_country_code'] = doc['mobile_country_code']
                self.dict['country'] = doc['country']
                self.dict['geo_location'] = doc['geo_location']
                self.dict['national_format'] = doc['national_format']

                self.dict['number'] = doc['number']

            return self.dict

        # when number is not in db
        else:
            data_from_twilio = self.obj.caller_data(number)
            # print('*')
            # print(data_from_twilio)
            self.db_loader(data_from_twilio)
            return data_from_twilio

    def db_loader(self, data):
        # print(data)

        d = {"carrier_name": data['carrier_name'],
             "mobile_network_code": data['mobile_network_code'],
             "country_code": data['country_code'],
             "number_type": data['number_type'],
             "mobile_country_code": data['mobile_country_code'],
             "country": data['country'],
             "geo_location": data['geo_location'],
             "national_format": data['national_format'],
             "number": data['number']
             }
        self.collection.insert_one(d)

        # close db connection
        self.client.close()


if __name__ == '__main__':
    obj = CallerInfo()
    print(obj.db_check("917727933442"))
# +97433013503
