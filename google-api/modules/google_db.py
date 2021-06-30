from pymongo import MongoClient
from modules.emailChecker import EmailChecker
from config import Config


class Google_db:

    def __init__(self):

        self.client = MongoClient(Config.MONGO_URI)
        db = self.client.google_db
        self.collection = db.data
        self.lst1 = []

    def db_check(self, emailId):

        for i in self.collection.find({}):
            # print(i)
            if i['email_id'] == emailId:
                self.lst1.append(i)
            else:
                pass
        # when data isn't present in db
        if len(self.lst1) == 0:

            obj = EmailChecker()
            t_data = obj.checker(emailId)
            # return t_data
            # print(t_data)

            # when google profile exists
            if 'email_id' in t_data.keys():

                # print(t_data['email_id'])
                # print(t_data['profileExists'])
                # print(t_data['name'])
                # print(t_data['image'])
                # print(t_data['googlePlusId'])

                self.data_loader(t_data)
                return t_data

            else:
                # print(t_data)
                return t_data

        # data directly from db
        else:
            # print(type(self.lst1[0]))
            return self.lst1[0]

    def data_loader(self, data):

        # print(data)
        # print(data['email'])
        # print(data['name'])
        # print(data['image'])
        # print(data['googlePlusId'])

        d = {"name": data['name'],
             "email": data['email'],
             "image": data['image'],
             # "googlePlusId": data['googlePlusId'],
             "email_id": data['email_id']
             }
        self.collection.insert_one(d)

        # close db connection
        self.client.close()


if __name__ == '__main__':
    obj = Google_db()
    # obj.data_loader({"name": "abdhf"})
    print(obj.db_check("justinmat1994@gmail.com"))

# justinmat1994@gmail.com
# abhaychatterjee1@gmail.com
