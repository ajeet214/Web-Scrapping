from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import requests

from config import Config


class EmailNumberChecker:

    def _get_proxy(self):
        url = "http://credsnproxy/api/v1/proxy"
        try:
            req = requests.get(url=url)
            if req.status_code != 200:
                raise ValueError
            return req.json()
        except:
            return {"proxy_host": '185.193.36.122',
                    "proxy_port": '23343'}

    def __init__(self):

        self.cred = self._get_proxy()
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        # options.add_argument('--proxy-server=socks://' + self.cred['proxy_host'] + ':' + self.cred['proxy_port'])

        # self.driver = webdriver.Chrome(chrome_options=options)

        # remote webdriver
        self.driver = webdriver.Remote(
            command_executor='http://' + Config.SELENIUM_CONFIG['host'] + ':' + Config.SELENIUM_CONFIG[
                'port'] + '/wd/hub',
            desired_capabilities=options.to_capabilities(),
        )

        self.EMAILFIELD = (By.ID, "identify_email")
        self.SUBMITBUTTON = (By.NAME, "did_submit")


    def Checker(self, emailId):
        url = "https://www.facebook.com/login/identify?ctx=recover&lwv=110"
        self.driver.get(url)
        sleep(0.5)
        # print(emailId)

        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.EMAILFIELD)).send_keys(emailId)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.SUBMITBUTTON)).click()
        # print("%s seconds" % (time.time() - start_time))
        sleep(2)
        try:
            mailid = self.driver.find_element_by_xpath('//div[@id="initiate_interstitial"]/div[2]/table/tbody/tr/td[2]/div/div/div[2]/div')
            sleep(0.5)
            q = mailid.text
            # print(q)
            self.driver.quit()
            # if q == emailId:
            #     return {'emailId_or_number': True}
            # elif q == '+' + emailId:
            return {'profileExists': True,
                    'profile_id/num': emailId}
        except:
            self.driver.quit()

            return {'profileExists': False}

    def fbEmailChecker(self, emailId):
        url = "https://www.facebook.com/login/identify?ctx=recover&lwv=110"
        self.driver.get(url)
        sleep(0.5)
        # print(emailId)

        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.EMAILFIELD)).send_keys(emailId)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.SUBMITBUTTON)).click()
        # print("%s seconds" % (time.time() - start_time))
        sleep(0.5)
        try:
            mailid = self.driver.find_element_by_xpath('//div[@id="initiate_interstitial"]/div[2]/table/tbody/tr/td[2]/div/div/div[2]/div')
            sleep(0.5)
            id_name = mailid.text
            # print(id_name)
            self.driver.quit()
            if id_name == emailId:
                return {'emailId': True}
        except:
            self.driver.quit()
            return {'emailId': False}

    def fbPhoneChecker(self, number):
        url = "https://www.facebook.com/login/identify?ctx=recover&lwv=110"
        self.driver.get(url)
        sleep(0.5)
        # print(number)

        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.EMAILFIELD)).send_keys(number)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.SUBMITBUTTON)).click()
        # print("%s seconds" % (time.time() - start_time))
        sleep(0.5)
        try:
            print('*')
            mailid = self.driver.find_element_by_xpath('//div[@id="initiate_interstitial"]/div[2]/table/tbody/tr/td[2]/div/div/div[2]/div')
            sleep(0.5)
            id_name = mailid.text
            # print(id_name)
            # if id_name == '+'+number:
            #     print('true')
            return {'contact_number': True}
        except:
            return {'contact_number': False}


if __name__ == '__main__':
    obj = EmailNumberChecker()
    # print(obj.fbEmailChecker('ajeet.verma214@gmail.com'))
    # print(obj.fbPhoneChecker('+919416284225'))
    print(obj.Checker('917726933452'))

    # obj.driver.quit()
# 917726933452
# 917726933451
