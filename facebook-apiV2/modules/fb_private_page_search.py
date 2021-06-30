from selenium import webdriver
from time import sleep
import time
import json
from bs4 import BeautifulSoup
import urllib.parse
import demjson
from requests_futures.sessions import FuturesSession
from concurrent.futures import ThreadPoolExecutor
from credential import creds
from config import Config
import asyncio


class PrivatePage:

    def __init__(self):
        self.session = FuturesSession(executor=ThreadPoolExecutor(max_workers=5))

        # cookies ='[{"domain":".facebook.com","hostOnly":false,"httpOnly":false,"name":"act","path":"/","sameSite":"no_restriction","secure":true,"session":true,"storeId":"1","value":"1543146867630%2F8","id":1},{"domain":".facebook.com","expirationDate":1550922837.861934,"hostOnly":false,"httpOnly":false,"name":"c_user","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"1","value":"100030701911575","id":2},{"domain":".facebook.com","expirationDate":1606218843.502958,"hostOnly":false,"httpOnly":true,"name":"datr","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"1","value":"WI36W7HlP3P1L_Qo7eiVHG6C","id":3},{"domain":".facebook.com","expirationDate":1550922837.861957,"hostOnly":false,"httpOnly":true,"name":"fr","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"1","value":"4Qa9p0o1OJ3fxji7F.AWV2giS-Ff_qIumFnMiNypDyBy0.Bb-o1V.ct.AAA.0.0.Bb-o1V.AWXcSWz6","id":4},{"domain":".facebook.com","expirationDate":1550922837.861968,"hostOnly":false,"httpOnly":true,"name":"pl","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"1","value":"n","id":5},{"domain":".facebook.com","hostOnly":false,"httpOnly":false,"name":"presence","path":"/","sameSite":"no_restriction","secure":true,"session":true,"storeId":"1","value":"EDvF3EtimeF1543146895EuserFA21B30701911575A2EstateFDutF1543146895966CEchFDp_5f1B30701911575F2CC","id":6},{"domain":".facebook.com","expirationDate":1606218837.861914,"hostOnly":false,"httpOnly":true,"name":"sb","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"1","value":"VY36W_EACAaYK3AHbTbTi6IU","id":7},{"domain":".facebook.com","expirationDate":1543236839.311551,"hostOnly":false,"httpOnly":true,"name":"spin","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"1","value":"r.4560428_b.trunk_t.1543146839_s.1_v.2_","id":8},{"domain":".facebook.com","expirationDate":1543751644,"hostOnly":false,"httpOnly":false,"name":"wd","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"1","value":"1920x927","id":9},{"domain":".facebook.com","expirationDate":1550922837.861946,"hostOnly":false,"httpOnly":true,"name":"xs","path":"/","sameSite":"no_restriction","secure":true,"session":false,"storeId":"1","value":"26%3ARhCvUlU4ziX5Eg%3A2%3A1543146838%3A-1%3A-1","id":10}]'
        self.Cookies = json.loads(creds['cookies'])
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extension")
        prefs = {"profile.default_content_setting_values.notifications": 2}
        options.add_experimental_option("prefs", prefs)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # options.add_argument("--headless")
        # self.driver = webdriver.Chrome(options=options)

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

    def fb_pages(self, query):

        query = urllib.parse.quote(query)

        self.driver.get('https://www.facebook.com/search/pages/?q='+query)
        sleep(1)
        for i in range(5):
            self.driver.execute_script("window.scrollTo(0, 19440)")
            sleep(1)

        # print(self.driver.page_source)
        # posts = driver.find_elements_by_class_name("_5bl2 _3u1 _41je")
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        # print(soup.prettify())

        self.driver.quit()

        return self.data_processing(soup)

    def data_processing(self, soup):
        list1 = []
        # location_list = []
        starting_path = soup.find('div', id='pagelet_loader_initial_browse_result')
        for each_element in starting_path.find_all('span', class_='_5bl2'):
        #     res = {}
            temp = dict()
            box = each_element.find('div', class_='clearfix _ikh')
            
            box1 = box.find('div', class_='_4bl7 _3-90')
            image = box1.a.img['src']
            temp['image'] = image
            url = box1.a['href']

            temp['url'] = url.replace('/?ref=br_rs', '')
            userid = temp['url'].split('/')[-1]
            temp['userid'] = userid

            box2 = box.find('div', class_='_4bl9')
            # header = box2.find('div', class_='clearfix').find('div', class_='_gll').find('a', class_='_32mo')
            header = box2.find('div', class_='_gll').find('a', class_='_32mo')
            # page name
            name = header.text
            temp['name'] = name

            # check if the page is verified or not
            try:
                verified = header.find('span')
                if verified.span['data-tooltip-content'].startswith('Verified'):
                    temp['verified'] = True
            except TypeError:
                temp['verified'] = False

            description = box2.find('div', class_='_glo').text
            temp['description'] = description
            # when description is not available
            if not temp['description']:
                temp['description'] = None

            other_details = box2.find('div', class_='_glm').text
            # temp['other_details'] = other_details

            temp['location'] = '@'

            # 1st format
            if other_details.startswith('Page'):
                temp['likes'] = other_details.split('·')[1].replace('\xa0', '').replace('like this', '').replace(
                    'likes this', '').replace(' ', '')

                if 'K' in temp['likes']:
                    temp['likes'] = int(float(temp['likes'].replace('K', ''))*1000)
                elif 'M' in temp['likes']:
                    temp['likes'] = int(float(temp['likes'].replace('M', '')) * 1000000)

                temp['category'] = other_details.split('·')[2].replace('\xa0', '')
                temp['location'] = '@'

            # 2nd format
            elif 'like' in other_details.split('·')[0]:
                temp['likes'] = other_details.split('·')[0].replace('\xa0', '').replace('like this', '').replace(
                    'likes this', '').replace(' ', '')

                if 'K' in temp['likes']:
                    temp['likes'] = int(float(temp['likes'].replace('K', '')) * 1000)
                elif 'M' in temp['likes']:
                    temp['likes'] = int(float(temp['likes'].replace('M', '')) * 1000000)

                try:
                    temp['location'] = other_details.split('·')[1].replace('\xa0', '')
                    temp['category'] = other_details.split('·')[2].replace('\xa0', '')
                # when location is not mentioned, only category
                except IndexError:
                    temp['category'] = other_details.split('·')[1].replace('\xa0', '')
                    temp['location'] = '@'

            temp['type'] = 'page'
            list1.append(temp)

        # print(list1)
        # return list1
        # ------------------------------------------------

        #     # print(div_1.find('a', class_='_32mo').text)
        #     res['name'] = div_1.find('a', class_='_32mo').text
        #     tem = div_1.find('a', class_='_32mo')
        #     try:
        #         temp = tem.find('span')
        #         verified = temp.find('span')
        #         res['verified'] = verified.text
        #         res['verified'] = True
        #     except:
        #         res['verified'] = False
        #     # print(div_1.find('div', class_='_4bl7 _3-90').a['href'])
        #     # print(div_1.find('a', class_='_32mo')['href'])
        #     res['url'] = div_1.find('a', class_='_32mo')['href'][:-10]
        #
        #     temp['url'] = res['url']
        #     # print(div_1.find('div', class_='_4bl7 _3-90').img['src'])
        #     res['image'] = div_1.find('div', class_='_4bl7 _3-90').img['src']
        #     a = div_1.find('div', class_='_glm')
        #     # print(a.text.split('·')[-1])
        #     try:
        #         res['category'] = (a.text.split('·')[-1])
        #     except:
        #         pass
        #     if len(a.text.split('·')) > 2:
        #         # print(a.text.split('·')[-2])
        #         res['location'] = a.text.split('·')[-2]
        #         temp['location'] = res['location']
        #         print(temp['location'])
        #         location_list.append(temp)
        #
        #     list2 = []
        #     for each_a in a.find_all('a'):
        #         # print(each_a.text)
        #         if 'like this' in each_a.text:
        #             res['likes'] = each_a.text.replace('like this', '').replace(' ', '')
        #
        #             if res['likes'].endswith('K'):
        #                 res['likes'] = float(res['likes'].replace('K', ''))*1000
        #                 res['likes'] = int(res['likes'])
        #
        #             elif res['likes'].endswith('M'):
        #                 res['likes'] = float(res['likes'].replace('M', ''))*1000000
        #                 res['likes'] = int(res['likes'])
        #
        #             else:
        #                 res['likes'] = int(res['likes'])
        #
        #         elif 'likes this' in each_a.text:
        #             res['likes'] = each_a.text.replace('likes this','').replace(' ', '')
        #
        #             if res['likes'].endswith('K'):
        #                 res['likes'] = float(res['likes'].replace('K', ''))*1000
        #                 res['likes'] = int(res['likes'])
        #
        #             elif res['likes'].endswith('M'):
        #                 res['likes'] = float(res['likes'].replace('M', ''))*1000000
        #                 res['likes'] = int(res['likes'])
        #
        #             else:
        #                 res['likes'] = int(res['likes'])
        #
        #         else:
        #             res['likes'] = None
        #
        #     string = div_1.find('div', class_='_glo')
        #     try:
        #         for each_item in string.find_all('div', class_='_ajw'):
        #             txt = each_item.find('div', class_='_52eh')
        #             content = txt.find('span')
        #             res['description'] = content.text
        #
        #     except:
        #         res['description'] = None
        #     res['type'] = 'page'
        #
        #     # print('***********')
        #     list1.append(res)
        # # print(location_list)
        # return list1
        # -------------------------------------------------------

        rs = []
        # print(list1)
        for u in list1:
            rs.append(self.session.get('https://maps.google.com/maps/api/geocode/json?address=' + str(
                u['location']) + '&key='+creds['google_map_key']))

        results = []
        for response in rs:
            temp_dict = dict()
            try:
                r = response.result()
                lt = demjson.decode(r.content.decode('utf-8'))
                # print(lt)
                # print(lt['results'][0]['address_components'])

                for i in lt['results'][0]['address_components']:
                    if i['types'][0] == 'country':
                        # print(i['long_name'])
                        temp_dict['country_code'] = i['short_name']
                        temp_dict['country'] = i['long_name']
                        results.append(temp_dict)
            # when the location is not available
            except IndexError:
                temp_dict['country_code'] = None
                temp_dict['country'] = None
                results.append(temp_dict)

        # print(results)

        for i in range(len(list1)):
            list1[i]['country_code'] = results[i]['country_code']
            list1[i]['country'] = results[i]['country']

            if list1[i]['location'] == '@':
                list1[i]['location'] = None

        return list1

        # return {'data':
        #         {'results': list1
        #          }
        #         }


if __name__ == '__main__':
    obj = PrivatePage()
    # print(obj.fb_pages('california'))
    print(obj.fb_pages('paul smith'))
