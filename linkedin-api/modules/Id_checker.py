from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from config import Config
from modules.caps_client import CapsClient
from time import sleep


class LinkedinId:

    def __init__(self):

        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--incognito")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extension")
        options.add_argument("--proxy-server={}".format(self._get_proxy()))

        # local webdriver
        # self.driver = webdriver.Chrome(options=options)

        # remote webdriver
        self.driver = webdriver.Remote(
            command_executor=Config.SELENIUM_URI,
            desired_capabilities=options.to_capabilities(),
        )

        self.EMAILFIELD = (By.ID, "username")
        self.PASSWORDFIELD = (By.ID, "password")

    # random proxy based on chosen filters
    def _get_proxy(self):

        try:
            random_proxy = CapsClient().get_proxy_random(type='socks5')
            print(random_proxy)
            return "socks5://{}:{}".format(random_proxy['host'], random_proxy['port'])

        except:
            return 'socks5://45.76.44.175:4899'

    def id_check(self, id):

        # url = 'https://www.linkedin.com/uas/request-password-reset?session_redirect=&trk=uas-login-forgot-password-text'
        url = 'https://www.linkedin.com/uas/login'
        self.driver.get(url)
        sleep(0.3)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.EMAILFIELD)).send_keys(id)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.PASSWORDFIELD)).send_keys('efknjkn@309')
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.PASSWORDFIELD)).send_keys(Keys.ENTER)

        sleep(0.3)
        # try:
        # pass_ = self.driver.find_element_by_id('session_password-login-error')
        pass_ = self.driver.find_element_by_id('error-for-password')
        txt = pass_.text
        # pwd = self.driver.find_element_by_xpath('//*[@id="session_key-login-error"]')
        pwd = self.driver.find_element_by_xpath('//*[@id="error-for-username"]')
        txt2 = pwd.text

        if txt.startswith("Hmm, that's not the right password"):
            self.driver.quit()
            return {'profileExists': True,
                    'profile': id}

        elif txt2.startswith("We don't recognize that email."):
            self.driver.quit()
            return {'profileExists': False,
                    'profile': id}

        elif txt2.startswith("Hmm, we don't recognize that email."):
            self.driver.quit()
            return {'profileExists': False,
                    'profile': id}


if __name__ == '__main__':
    obj = LinkedinId()
    print(obj.id_check('quality.slip2016@ydex.com'))


# pparkar549@gmail.com
# jaqsoms43@gmail.com
