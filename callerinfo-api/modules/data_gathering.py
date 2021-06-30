import requests
from bs4 import BeautifulSoup


class DataSheet:

    def __init__(self):

        url = 'https://developers.google.com/public-data/docs/canonical/countries_csv'
        a = requests.get(url)
        self.soup = BeautifulSoup(a.text, 'lxml')
        # print(soup.prettify())

    def data_extractor(self):
        b = self.soup.find('table')
        list2 = []
        for each_tr in b.find_all('tr'):
            list1 = []
            dict1 = {}
            for i in each_tr.find_all('th'):
                list1.append(i.text)

            for i in each_tr.find_all('td'):
                # print(i.text)
                list1.append(i.text)
            # print(list1)

            dict1['country'] = list1[0]
            dict1['latitude'] = list1[1]
            dict1['longitude'] = list1[2]
            dict1['name'] = list1[3]
            list2.append(dict1)

        return list2[1:]


if __name__ == "__main__":
    obj = DataSheet()
    print(obj.data_extractor())
