from selenium import webdriver
import os
import json
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from pymongo import MongoClient
from config import Config
from bs4 import BeautifulSoup as bs
from credentials import cookies
from modules.caps_client import CapsClient


class GoogleContacts:

    # random proxy based on chosen filters
    def _get_proxy(self):

        try:
            random_proxy = CapsClient().get_proxy_random(type='socks5')
            print(random_proxy)
            return "socks5://{}:{}".format(random_proxy['host'], random_proxy['port'])

        except:
            return 'socks5://89.39.107.101:80'
            # '45.76.44.175:4899'

    def _get_cookies(self):
            return {'cookies': cookies['cookies']}

    def __init__(self):

        self.client = MongoClient(Config.MONGO_URI)
        db = self.client.contacts
        self.collection = db.data
        # self.cred = self._get_proxy()
        self.cred = self._get_cookies()
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        # options.add_argument("--incognito")
        options.add_argument("--proxy-server={}".format(self._get_proxy()))

        self.Cookies = json.loads(self.cred['cookies'])

        # chrome webdriver
        # self.driver = webdriver.Chrome(options=options)

        # remote webdriver
        self.driver = webdriver.Remote(
            command_executor=Config.SELENIUM_URI,
            desired_capabilities=options.to_capabilities(),
        )

        # self.EMAILFIELD = (By.ID, "identifierId")
        # self.PASSWORDFIELD = (By.NAME, "password")
        # self.NEXTBUTTON = (By.ID, "identifierNext")
        # self.PNEXTBUTTON = (By.ID, "passwordNext")
        self.SEARCHFIELD = (By.NAME, "q")
        self.SUBMIT = (By.CLASS_NAME, "gbqfb")

    def checker(self, numbers):

        # for i in numbers['number_list']:
        #     print(i)

        filePath = '/home/python1/Dukto/contacts.csv'

        # remove if the file exists
        if os.path.exists(filePath):
            os.remove(filePath)

        # create and open the file to write
        the_file = open(filePath, 'w+')
        the_file.write(
            'Name,Given Name,Additional Name,Family Name,Yomi Name,Given Name Yomi,Additional Name Yomi,Family Name Yomi,Name Prefix,Name Suffix,Initials,Nickname,Short Name,Maiden Name,Birthday,Gender,Location,Billing Information,Directory Server,Mileage,Occupation,Hobby,Sensitivity,Priority,Subject,Notes,Language,Photo,Group Membership,Phone 1 - Type,Phone 1 - Value\n')

        for i in numbers['number_list']:
            the_file.write(',,,,,,,,,,,,,,,,,,,,,,,,,,,,,,+{}{}'.format(i, '\n'))
        the_file.close()

        # print(open(filePath).readlines())
        final_list = []

        self.driver.get("https://google.com")

        for cookie in self.Cookies:
            cookie_dict = {'domain': cookie['domain'], 'secure': cookie['secure'], 'value': cookie['value'],
                           'name': cookie['name'], 'httpOnly': cookie['httpOnly'], 'storeId': cookie['storeId'],
                           'path': cookie['path'], 'session': cookie['session'], 'hostOnly': cookie['hostOnly'],
                           'sameSite': cookie['sameSite'], 'id': cookie['id']}
            try:
                if cookie['expirationDate']:
                    cookie_dict['expirationDate'] = cookie['expirationDate']
                    # print(cookie['expirationDate'])
            except:
                pass
            # print(cookie_dict)
            # loading cookies to webdriver
            self.driver.add_cookie(cookie_dict)

        sleep(0.5)
        # self.driver.get('https://gmail.com')
        self.driver.get('https://contacts.google.com/')
        self.driver.find_element_by_xpath('//*[@id="yDmH0d"]/c-wiz/div[2]/div[5]/div[2]/div/div/div[3]/button[2]/span[2]').click()
        sleep(0.5)
        self.driver.find_element_by_xpath('//*[@id="yDmH0d"]/div[4]/div/div[2]/content/div/label/div')
        sleep(0.2)
        self.driver.find_element_by_name('file').send_keys('/home/python1/Dukto/contacts.csv')
        sleep(0.2)
        self.driver.find_element_by_xpath('//*[@id="yDmH0d"]/div[4]/div/div[2]/div[3]/div/button[2]/span').click()
        sleep(3)

        # self.driver.execute_script("""
        #     e_list = document.getElementsByTagName('c-wiz');
        #     i = e_list.length - 1
        #     elem = e_list[i]
        #     elem.addEventListener('scroll', function(event){
        #         elem.scrollBy(0,100)
        #     })
        #     elem.scrollBy(0,100)
        #
        # """)
        # sleep(2)
        # print(self.driver.page_source)

        # soup = bs(self.driver.page_source, 'html.parser')
        # print(soup.prettify())

        # iterating over all the contacts
        c = 0
        for i in self.driver.find_elements_by_class_name('XXcuqd'):
            temp_dict = dict()
            c += 1
            temp_list = []
            # print(i.find_element_by_tag_name('img').get_attribute('src').replace('=s36-p-k-rw-no', ''))
            image = i.find_element_by_tag_name('img').get_attribute('src').replace('=s36-p-k-rw-no', '')
            temp_list.append(image)

            for j in i.find_elements_by_class_name('E6Tb7b'):
                # print(j.text)
                temp_list.append(j.text)

            print(temp_list)
            # when name and number both are same i.e both r number
            if temp_list[2] == temp_list[3]:
                pass
            # when its number at the place of name
            elif temp_list[2].replace('+', '').isnumeric():
                pass
            #  when its name
            else:
                temp_dict['image'] = temp_list[0]
                if 'AAAAAAAAAAI/AAAAAAAAAAA/' in temp_dict['image']:
                    temp_dict['image'] = None

                temp_dict['name'] = temp_list[2]

                temp_dict['number'] = int(temp_list[3].replace('+', ''))

                temp_dict['email'] = temp_list[4]
                if not temp_dict['email']:
                    temp_dict['email'] = None

                temp_dict['address'] = temp_list[5]
                if not temp_dict['address']:
                    temp_dict['address'] = None

                temp_dict['dob'] = temp_list[6]
                if not temp_dict['dob']:
                    temp_dict['dob'] = None

                final_list.append(temp_dict)
            # print('*')

        print(c)

        sleep(1)
        # click to remove the contact list
        self.driver.find_element_by_xpath('//*[@id="gb"]/div[4]/div[2]/c-wiz/div/span/span/div/div/div/div[2]').click()
        sleep(0.5)
        self.driver.find_element_by_xpath('//*[@id="yDmH0d"]/div[4]/div/div[2]/div[3]/div/button[2]/span').click()
        #
        self.driver.close()

        for i in final_list:

            if self.collection.find_one({'number': i['number']}):
                pass

            else:
                self.collection.insert_one(i)
            self.client.close()

        for i in final_list:
            print(i)
            try:
                if i['_id']:
                    del i['_id']
            except KeyError:
                pass
        return final_list


if __name__ == '__main__':
    obj = GoogleContacts()
    # justinmat1994@gmail.com
    print(obj.checker({"number_list": [919999368527,
                                       919416284225,
                                       917727933442,
                                       918860273361,
                                       919716404084,
                                       919026662367,
                                       919999368557,
                                       919999368597,
                                       919999368523,
                                       919999368522
                                       ]
                       }))


