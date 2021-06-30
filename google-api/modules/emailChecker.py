import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from time import sleep
from modules.caps_client import CapsClient

from credentials import cookies
from config import Config


class EmailChecker:

    def __init__(self):

        self.cap = CapsClient()
        self.cred = self._get_cookies()
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        # options.add_argument("--incognito")
        # options.add_argument('--proxy-server=socks://' + self.cred['proxy_host'] + ':' + self.cred['proxy_port'])
        options.add_argument("--proxy-server={}".format(self._get_proxy()))

        print("proxy:  {}".format(self._get_proxy()))

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

    # random proxy based on chosen filters
    def _get_proxy(self):

        try:
            random_proxy = self.cap.get_proxy_random(type='socks5')
            return "socks5://{}:{}".format(random_proxy['host'], random_proxy['port'])

        except:
            return 'socks5://5.39.20.153:25567'

    def _get_cookies(self):
        credential = self.cap.get_credential_random('google')
        return {'cookies': cookies['cookies']}

    def checker(self, emailId):

        url = "https://gmail.com/"
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
            self.driver.add_cookie(cookie_dict)
        sleep(0.5)
        self.driver.get('https://gmail.com')

        # print(emailId)
        #
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.SEARCHFIELD)).send_keys(emailId)
        # WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.SUBMIT)).click()
        self.driver.find_element_by_name('q').send_keys(Keys.ENTER)
        # WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.PASSWORDFIELD)).send_keys(passd)
        # WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.PNEXTBUTTON)).click()
        # # print("%s seconds" % (time.time() - start_time))
        sleep(3)
        try:

            # # googleplusid
            try:
                mailid1 = self.driver.find_element_by_xpath('//*[@id=":2"]/div/div[2]/div[4]/div[1]/div[2]/div[1]/div[1]')
            except NoSuchElementException:
                mailid1 = self.driver.find_element_by_xpath('//*[@id=":1"]/div/div[2]/div[4]/div[1]/div[2]/div[1]/div[1]')
            # # sleep(0.5)
            # print(mailid1)
            # e = mailid1.get_attribute('href')
            # image on google account
            try:
                image = self.driver.find_element_by_xpath('//*[@id=":2"]/div/div[2]/div[4]/div[1]/div[1]/img')
            except NoSuchElementException:
                image = self.driver.find_element_by_xpath('//*[@id=":1"]/div/div[2]/div[4]/div[1]/div[1]/img')
            img = image.get_attribute('src')
            # print(e)
            # name of the user
            name = mailid1.text
            self.driver.quit()

            return {'email': True,
                    'email_id': emailId,
                    # 'googlePlusId': e[24:],
                    'name': name,
                    'image': img}
        except:
            self.driver.quit()
            return {'email': False}

        # # try:
        #     mailid1 = self.driver.find_element_by_xpath('//*[@id="app__container"]/div[2]/header')
        #     sleep(0.5)
        #     print(mailid1.text)
        #     self.driver.quit()
        #
        #     return {'mailid': False}
        # except:
        #     mailid = self.driver.find_element_by_xpath('//*[@id="signup_magiclink"]/div[1]/div/h1/p')
        #     sleep(2)
        #     print(mailid.text)
        #     self.driver.quit()
        #
        #     return {'mailid': True}


if __name__ == '__main__':
    obj = EmailChecker()
    # print(obj.checker('veronikascott27@gmail.com'))
    print(obj.checker('justinmat1994@gmail.com'))
    # print(obj.checker('justinmat199@gmail.com'))

