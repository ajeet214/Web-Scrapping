from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import requests
from modules.caps_client import CapsClient
from config import Config


class EmailChecker:

    def __init__(self):

        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--incognito")
        options.add_argument("--proxy-server={}".format(self._get_proxy()))
        # options.add_argument('--proxy-server=socks://' + self.cred['proxy_host'] + ':' + self.cred['proxy_port'])

        # self.driver = webdriver.Chrome(chrome_options=options)

        # remote webdriver
        self.driver = webdriver.Remote(
            command_executor=Config.SELENIUM_URI,
            desired_capabilities=options.to_capabilities(),
        )

        self.EMAILFIELD = (By.NAME, "account_identifier")
        self.SUBMITBUTTON = (By.CLASS_NAME, "Button EdgeButton--primary EdgeButton")

    # random proxy based on chosen filters
    def _get_proxy(self):

        try:
            random_proxy = CapsClient().get_proxy_random(type='socks5')
            print(random_proxy)
            return "socks5://{}:{}".format(random_proxy['host'], random_proxy['port'])

        except:
            return 'socks5://45.76.44.175:4899'

    def checker(self, emailId):
        url = "https://twitter.com/account/begin_password_reset"
        self.driver.get(url)
        sleep(0.5)
        # print(emailId)

        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.EMAILFIELD)).send_keys(emailId)
        # WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.SUBMITBUTTON)).click()
        self.driver.find_element_by_xpath('/html/body/div[2]/div/form/input[3]').click()
        # # # print("%s seconds" % (time.time() - start_time))
        sleep(0.5)

        mailid1 = self.driver.find_element_by_xpath('/html/body/div[2]/div/div[1]')
        print(mailid1.text)
        sleep(0.5)
        # return {'mailid': False}
        if 'How do you want to reset your password?' in mailid1.text:
            print('pass')

            self.driver.quit()
            return {'profileExists': True,
                    'contacts': emailId}
        elif "We couldn't find your account with that information" in mailid1.text:
            print('fail')

            self.driver.quit()
            return {'profileExists': False}

        elif "We found more than one account with that phone number" in mailid1.text:
            print('more than one account')

            self.driver.quit()
            return {'profileExists': True,
                    'contacts': emailId}


        # # try:
        # #     mailid1 = self.driver.find_element_by_xpath('//*[@id="app__container
        #

        # "]/div[2]/header')
        # #     sleep(0.5)
        # #     print(mailid1.text)
        # #     self.driver.quit()
        # #
        # #     return {'mailid': False}
        # except:
        #     mailid = self.driver.find_element_by_xpath('/html/body/div[2]/div/div[1]')
        #     print(mailid.text)
        #     self.driver.quit()


if __name__ == '__main__':
    obj = EmailChecker()
    print(obj.checker('justinmat1994@outlook.com'))

# 919166333537
# justinmat1994@outlook.com