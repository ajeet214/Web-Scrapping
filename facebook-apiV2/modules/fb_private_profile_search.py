from selenium import webdriver
from time import sleep
import time
import json
from bs4 import BeautifulSoup
import urllib.parse
from credential import creds
from config import Config

class PrivateProfile:

    def __init__(self):

        # cookies ='[{"domain":".facebook.com","expirationDate":1547965700.831146,"hostOnly":false,"httpOnly":false,"name":"c_user","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"1","value":"100024661938863","id":1},{"domain":".facebook.com","expirationDate":1603261707.013212,"hostOnly":false,"httpOnly":true,"name":"datr","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"1","value":"BW7NWzL1UMFj84xLxkBeG2Od","id":2},{"domain":".facebook.com","expirationDate":1547965707.84508,"hostOnly":false,"httpOnly":true,"name":"fr","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"1","value":"3beFuiAqg7OXys1ii.AWVU8qkDRTusLurdjUuJuHXEEGc.BbzW4E.eF.FvN.0.0.BbzW4L.AWUbfHh7","id":3},{"domain":".facebook.com","expirationDate":1547965700.831266,"hostOnly":false,"httpOnly":true,"name":"pl","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"1","value":"n","id":4},{"domain":".facebook.com","hostOnly":false,"httpOnly":false,"name":"presence","path":"/","sameSite":"no_restriction","secure":true,"session":true,"storeId":"1","value":"EDvF3EtimeF1540189708EuserFA21B24661938863A2EstateFDutF1540189708165CEchFDp_5f1B24661938863F2CC","id":5},{"domain":".facebook.com","expirationDate":1603261700.831105,"hostOnly":false,"httpOnly":true,"name":"sb","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"1","value":"BG7NW6XzviASY6T9_49JoP7M","id":6},{"domain":".facebook.com","expirationDate":1540279702.05565,"hostOnly":false,"httpOnly":true,"name":"spin","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"1","value":"r.4445831_b.trunk_t.1540189701_s.1_v.2_","id":7},{"domain":".facebook.com","expirationDate":1540794507,"hostOnly":false,"httpOnly":false,"name":"wd","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"1","value":"1920x927","id":8},{"domain":".facebook.com","expirationDate":1547965700.831192,"hostOnly":false,"httpOnly":true,"name":"xs","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"1","value":"42%3AuO4dyzOaTPCecw%3A2%3A1540189700%3A20790%3A9860","id":9}]'
        self.Cookies = json.loads(creds['cookies'])
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        # options.add_argument("--headless")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extension")
        prefs = {"profile.default_content_setting_values.notifications": 2}
        options.add_experimental_option("prefs", prefs)

        # self.driver = webdriver.Chrome(chrome_options=options)

        # remote webdriver
        self.driver = webdriver.Remote(
            command_executor='http://' + Config.SELENIUM_CONFIG['host'] + ':' + Config.SELENIUM_CONFIG[
                'port'] + '/wd/hub',
            desired_capabilities=options.to_capabilities(),
        )

        url = "http://www.facebook.com"

        start_time = time.time()
        self.driver.get(url)

        for cookie in self.Cookies:
            # cookie_dict = {'domain': None, 'secure': cookie['secure'], 'value': cookie['value'],
            #                'name': cookie['name'], 'httpOnly': cookie['httpOnly'], 'storeId': cookie['storeId'],
            #                'path': cookie['path'], 'session': cookie['session'], 'hostOnly': cookie['hostOnly'],
            #                'sameSite': cookie['sameSite'], 'id': cookie['id']}
            # try:
            #     if cookie['expirationDate']:
            #         cookie_dict['expirationDate'] = cookie['expirationDate']
            #         # print(cookie['expirationDate'])
            # except:
            #     pass
            # # print(cookie_dict)
            # self.driver.add_cookie(cookie_dict)
            self.driver.add_cookie(cookie)

    def fb_profile(self, query):

        query = urllib.parse.quote(query)

        self.driver.get('https://www.facebook.com/search/people/?q='+query)
        sleep(1)
        self.driver.execute_script("window.scrollTo(0, 3240)")
        sleep(1)
        self.driver.execute_script("window.scrollTo(0, 3240)")
        sleep(1)
        self.driver.execute_script("window.scrollTo(0, 3240)")
        sleep(1)
        # print(driver.page_source)
        # posts = driver.find_elements_by_class_name("_5bl2 _3u1 _41je")
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        self.driver.quit()
        # print(soup)
        list_1 = []

        list1 = []
        for each_element in soup.find_all('div', class_='_4p2o'):
            res = {}
            div_1 = each_element.find('div', class_='clearfix _ikh')
            # print(div_1.find('a', class_='_32mo').text)
            title = div_1.find('a', class_='_32mo')
            res['name'] = title.text
            verified = title.find('span').span
            if verified == None:
                res['verified'] = False
            else:res['verified'] = True

            # try:
            #     res['varified'] = title.find('span', {'data-tooltip-content':'Verified PageFacebook confirmed that this is an authentic Page for this public figure, media company or brand.'})
            #     res['varified'] = True
            # except:
            #     res['varified'] = False
            # print(div_1.find('div', class_='_4bl7 _3-90').a['href'])
            # print(div_1.find('a', class_='_32mo')['href'])
            res['url'] = div_1.find('a', class_='_32mo')['href'][:-10]
            res['userid'] = res['url'].split('/')[-1]
            if 'profile.php?id' in res['userid']:
                res['userid'] = res['userid'][15:]
            # print(div_1.find('div', class_='_4bl7 _3-90').img['src'])
            res['image'] = div_1.find('div', class_='_4bl7 _3-90').img['src']
            lst = []
            list2 = []
            try:
                div_2 = div_1.find('div', class_='_glo')
                for each_item in div_2.find_all('div', class_='_ajw'):
                    list2.append(each_item.text)
                    # dict = {}
                    # print(each_item.text)
                    # dict['text'] = each_item.text
                    # try:
                    #     # print(each_item.a['href'])
                    #     dict['url'] = each_item.a['href']
                    # except:
                    #     pass
                    # list2.append(dict)
                # if list2[0] != '':
                #     res['details'] = list2
            except:
                pass

            try:
                a = div_1.find('div', class_='_glm').text
                # res['description'] = a
                lst.append(a)
                res['description'] = lst + list2
                res['description'] = ', '.join(str(e) for e in res['description'])

                    # print(a)
                # try:
                #     if div_1.find('div', class_='_glm').a['href']:
                #         # print('https://www.facebook.com'+div_1.find('div', class_='_glm').a['href'])
                #         res['description_url'] = div_1.find('div', class_='_glm').a['href']
                #         if res['description_url'].startswith('https'):
                #             res['description_url'] = div_1.find('div', class_='_glm').a['href']
                #         else:
                #             res['description_url'] = 'https://www.facebook.com'+div_1.find('div', class_='_glm').a['href']
                # except:
                #     pass
            except:
                pass
            if not res['description']:
                res['description'] = None
            res['type'] = 'identity'

            list1.append(res)
        return list1
        # return {'data':
        #         {'results': list1}
        #         }


if __name__ == '__main__':
    obj = PrivateProfile()
    print(obj.fb_profile('georgia'))
