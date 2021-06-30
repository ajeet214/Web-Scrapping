import yweather


class WOEID:

    def __init__(self):
        self.client = yweather.Client()

    def fetch_woeid(self, areaName):

       return self.client.fetch_woeid(areaName)


if __name__ == '__main__':
    obj = WOEID()
    print(obj.fetch_woeid("america"))
