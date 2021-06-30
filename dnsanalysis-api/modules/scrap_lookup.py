import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os

from config import Config
from credentials import creds
from config import Config


class ScrapLookup:

    def __init__(self):

        self.EMAILFIELD = (By.ID, "tbEmail")
        self.DOMAIN_FIELD = (By.ID, "focusedInput")
        self.PASSWORDFIELD = (By.ID, "tbPassword")
        self.NEXTBUTTON = (By.ID, "ctl00_ContentPlaceHolder1_btnLogIn")

        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extension")
        options.add_argument('--proxy-server=socks://' + '185.193.36.122' + ':' + '23343')

        # self.driver = webdriver.Chrome(chrome_options=options)

        # remote webdriver
        self.driver = webdriver.Remote(
            command_executor='http://' + Config.SELENIUM_CONFIG['host'] + ':' + Config.SELENIUM_CONFIG[
                'port'] + '/wd/hub',
            desired_capabilities=options.to_capabilities(),
        )

        # prefs = {"profile.default_content_setting_values.notifications": 2}
        # options.add_experimental_option("prefs", prefs)

    def check_pickle(self, lookup_type, domain_name):

        if os.path.isfile('cookies.pickle'):
            return self.getResult(lookup_type, domain_name)
        else:
            self.create_pickle()
            return self.getResult(lookup_type, domain_name)

    def create_pickle(self):

        self.driver.get("https://mxtoolbox.com/Public/Login.aspx")
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.EMAILFIELD)).send_keys(creds['email'])
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.PASSWORDFIELD)).send_keys(creds['password'])
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.NEXTBUTTON)).click()
        # print(driver.get_cookies())

        # saving cookies in pickle file
        with open('cookies.pickle', 'wb') as handle:
            pickle.dump(self.driver.get_cookies(), handle, protocol=pickle.HIGHEST_PROTOCOL)

        # pickle.dump(driver.get_cookies(), open("cookies.pickle", "wb"), protocol=pickle.HIGHEST_PROTOCOL)

    def getResult(self, lookup_type, domain_name):


        self.driver.get("https://mxtoolbox.com/Public/Login.aspx")

        # loading cookies
        cookies = pickle.load(open("cookies.pickle", "rb"))
        for cookie in cookies:
            self.driver.add_cookie(cookie)

        self.driver.get('https://api.mxtoolbox.com/api/v1/Lookup/' + lookup_type + '/?argument=' + domain_name)
        data = self.driver.page_source[121:-20]

        # print("%s seconds" % (time.time() - start_time))
        self.driver.quit()

        return json.loads(data)


if __name__ == '__main__':
    obj = ScrapLookup()
    print(obj.check_pickle('whois', 'mfa.gov.cn'))
    # print(obj.getResult('mx', 'twitter.com'))
