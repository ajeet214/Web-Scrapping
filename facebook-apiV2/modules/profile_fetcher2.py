import urllib.parse
import json
import time
from time import sleep
# import sys
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from config import Config
from credential import creds


class ProfileFetch:

    def _get_credentials(self):
        # change url as per credentials reequired
        url = "http://credsnproxy/api/v1/facebook"
        try:
            req = requests.get(url=url)
            if req.status_code != 200:
                raise ValueError
            return req.json()
        except:
            # return fallback object
            return {
                'cookies': creds['m_cookies']}

    def __init__(self):

        self.cred = self._get_credentials()
        self.cookies = json.loads(self.cred['cookies'])
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        # options.add_argument("--headless")
        prefs = {"profile.default_content_setting_values.notifications": 2}
        options.add_experimental_option("prefs", prefs)
        self.final_dict = dict()

        # local webdriver ------------
        # self.driver = webdriver.Chrome(options=options)

        # remote webdriver -----------
        self.driver = webdriver.Remote(
            command_executor='http://' + Config.SELENIUM_CONFIG['host'] + ':'
            + Config.SELENIUM_CONFIG['port'] + '/wd/hub',
            desired_capabilities=options.to_capabilities()
        )

        url = "https://m.facebook.com/home.php"

        self.driver.get(url)

        for cookie in self.cookies:
            # cookie_dict = {'domain': None,
            #                'secure': cookie['secure'],
            #                'value': cookie['value'],
            #                'name': cookie['name'],
            #                'httpOnly': cookie['httpOnly'],
            #                'storeId': cookie['storeId'],
            #                'path': cookie['path'],
            #                'session': cookie['session'],
            #                'hostOnly': cookie['hostOnly'],
            #                'sameSite': cookie['sameSite'],
            #                'id': cookie['id']}
            # # try:
            # #     if cookie['expirationDate']:
            # #         cookie_dict['expirationDate'] = cookie['expirationDate']
            # #         # print(cookie['expirationDate'])
            # # except:
            # #     pass
            # # print(cookie_dict)
            # self.driver.add_cookie(cookie_dict)
            self.driver.add_cookie(cookie)

    def image_formattor(self, image_path):

        formatted_url = image_path.i['style'][image_path.i['style'].index(
            '(') + 2:image_path.i['style'].index(')') - 1].replace(' ', '').replace(
            '\\3a', ':').replace('\\3d', '=').replace('\\26', '&').replace('\\25', '%')

        return formatted_url

    def fb_profile_fetch(self, query):

        query = urllib.parse.quote(query)
        self.driver.get('https://m.facebook.com/'+query)
        sleep(0.5)
        soup1 = BeautifulSoup(self.driver.page_source, 'html.parser')
        name_and_pic = soup1.find(class_='_42b6')
        self.final_dict['name'] = name_and_pic.i['aria-label']
        self.final_dict['profile_image'] = self.image_formattor(name_and_pic)

        self.driver.get('https://m.facebook.com/{}/about?lst=100031108780189%3A{}%3A{}'.format(query, query, int(time.time())))

        #previous version:  self.driver.find_element_by_link_text('About').click()
        sleep(1)

        self.driver.execute_script("window.scrollTo(0, 3240)")
        sleep(0.5)
        self.driver.execute_script("window.scrollTo(0, 3240)")

        soup2 = BeautifulSoup(self.driver.page_source, 'html.parser')
        # print(soup2.prettify())
        sleep(0.5)
        self.driver.close()
        # -------------------------------------------------------------

        # education ----------------------------------------
        try:
            education = soup2.find('div', id="education")
            edu_list = list()
            for i in education.find_all('div', class_="_5cds _2lcw"):
                college_name_dict = dict()
                college_name_dict['image'] = self.image_formattor(i)
                edu_temp_list = []
                for j in i.find_all('span'):
                    edu_temp_list.append(j.text)

                college_name_dict['datails'] = ','.join(edu_temp_list)
                edu_list.append(college_name_dict)

            self.final_dict['education'] = edu_list
        except:
            # print({"education": None})
            self.final_dict['education'] = None

        # work ---------------------------------------------
        try:
            work = soup2.find('div', id="work")
            work_list = list()
            for i in work.find_all('div', class_="_5cds _2lcw"):
                organisation_name_dict = dict()
                organisation_name_dict['image'] = self.image_formattor(i)
                work_temp_list = []
                for j in i.find_all('span'):
                    work_temp_list.append(j.text)

                organisation_name_dict['datails'] = ','.join(work_temp_list)
                work_list.append(organisation_name_dict)

            self.final_dict['work'] = work_list
        except:
            # print({"work": None})
            self.final_dict['work'] = None

        # living places -------------------------------------
        try:
            places_lived = soup2.find('div', id="living")
            places_list = list()

            for i in places_lived.find_all('div', class_="_2swz _2lcw"):
                sub_list = []
                for j in i.find_all('h4'):
                    sub_list.append(j.text)

                city_hometown = ', '.join(sub_list)
                places_img = self.image_formattor(i)
                # print(city_hometown)
                places_list.append({city_hometown.split(',')[-1]: city_hometown.replace(
                    city_hometown.split(',')[-1], ''), "image": places_img})

            for i in places_lived.find_all('div', class_="_55wr _4g33 _5b6o _2lcw touchable _592p _25mv"):
                sub_list = []
                for j in i.find_all('h4'):
                    sub_list.append(j.text)

                moved_to_places = ', '.join(sub_list)
                places_img = self.image_formattor(i)
                # print(city_hometown)
                places_list.append({moved_to_places.split(',')[-1]: moved_to_places.replace(
                    moved_to_places.split(',')[-1], ''), "image": places_img})

            self.final_dict['places_lived'] = places_list
        except:
            # print(sys.exc_info())
            self.final_dict['places_lived'] = None

        # contact-info ---------------------------------------
        try:
            contact_info = soup2.find('div', id="contact-info")
            contact_info_list = dict()
            for i in contact_info.find_all('div', class_="_5cds _2lcw _5cdu"):
                # print({i['title']: i.text.replace(i['title'], '')})
                contact_info_list[i['title']] = i.text.replace(i['title'], '')
            # print({"contact_info": contact_info_list})
            self.final_dict['contact_info'] = contact_info_list
        except:
            # print({"contact_info": None})
            self.final_dict['contact_info'] = None

        # basic-info ------------------------------------------
        try:
            basic_info = soup2.find('div', id="basic-info")
            basic_info_list = dict()
            for i in basic_info.find_all('div', class_="_5cds _2lcw _5cdu"):
                # print({i['title']: i.text.replace(i['title'], '')})
                basic_info_list[i['title']] = i.text.replace(i['title'], '')
            # print({"basic_info": basic_info_list})
            self.final_dict['basic_info'] = basic_info_list
        except:
            # print({"basic_info": None})
            self.final_dict['basic_info'] = None

        # relationship ---------------------------------------
        try:
            relationship = soup2.find('div', id="relationship").find('div', class_="_5cds")
            tem_list = []
            formatted_url = self.image_formattor(relationship)

            for i in relationship.find_all('h3'):
                tem_list.append(i.text)
            # print(','.join(tem_list))
            # print({"relationship": [', '.join(tem_list), {"relation_profile": relationship.a['href']}]})
            self.final_dict['relationship'] = [
                {"name": ', '.join(tem_list).split(',')[0],
                 "other_detail": ', '.join(tem_list).replace(', '.join(tem_list).split(',')[0], ''),
                 "profile_userid": relationship.a['href'][1:relationship.a['href'].index('?')],
                 "image": formatted_url
                 }
            ]
        except:
            # print({"relationship": None})
            self.final_dict['relationship'] = None

        # family_members -------------------------------------
        try:
            family_members = soup2.find('div', id="family")
            family_members_list = list()
            for i in family_members.find_all('div', class_="_5r7k _2lcw"):
                each_member = list()
                temp_dict = dict()
                temp_dict['profile_userid'] = i.a['href'][1:i.a['href'].index('?')]

                # when the user is not on fb
                if temp_dict['profile_userid'].startswith('scrapbooks'):
                    temp_dict['profile_userid'] = None

                formatted_url = self.image_formattor(i)
                temp_dict['image'] = formatted_url
                for j in i.find_all('h3'):
                    each_member.append(j.text)

                name_relation = ', '.join(each_member)
                temp_dict['name'] = name_relation.split(',')[0]
                temp_dict['relationship'] = name_relation.split(',')[1]
                family_members_list.append(temp_dict)
            # print({'family_members': family_members_list})
            self.final_dict['family_members'] = family_members_list
        except:
            # print({'family_members': None})
            self.final_dict['family_members'] = None

        # favourite quotes -----------------------------------------
        try:
            favourite_quote = soup2.find('div', id='quote').find('div', class_="_55x2 _5ji7")
            # print(favourite_quote.text)
            self.final_dict['favourite_quotes'] = favourite_quote.text
        except:
            self.final_dict['favourite_quotes'] = None

        # about bio ------------------------------------------------
        try:
            bio = soup2.find('div', id='bio').find('div', class_="_55x2 _5ji7")
            # print(bio.text)
            self.final_dict['about'] = bio.text
        except:
            self.final_dict['about'] = None

        # life events ----------------------------------------------
        try:
            life_events = soup2.find('div', id='year-overviews')
            life_events_dict = dict()
            for i in life_events.find_all('div', class_="_3-9b _3-92 _3-97"):
                events_list = list()
                # print(i.find('div', class_="_3-95 _3-8x").text)

                for j in i.find_all('div', class_="ib _3-8y _3-96"):
                    # print(j.text)
                    events_list.append(j.text)
                life_events_dict[i.find('div', class_="_3-95 _3-8x").text] = events_list

            self.final_dict['life_events'] = life_events_dict

        except:
            self.final_dict['life_events'] = None

        # skills --------------------------------------------------
        try:
            skills = soup2.find('div', id="skills").find('div', class_="_55x2 _5ji7")
            # print(skills.text)
            self.final_dict['professional_skills'] = skills.text
        except:
            self.final_dict['professional_skills'] = None

        # other names ---------------------------------------------
        try:
            other_names = soup2.find('div', id="nicknames").find('div', class_="_55x2 _5ji7")
            # print(other_names.span.text)
            self.final_dict[other_names.span.text] = other_names.text.replace(other_names.span.text, '')
        except:
            self.final_dict['other_name'] = None

        self.final_dict['profile_url'] = "https://www.facebook.com/{}".format(query)

        return self.final_dict


if __name__ == '__main__':
    OBJ = ProfileFetch()
    print(OBJ.fb_profile_fetch('cherylKikoMimko92'))


# senol.oezdemir1
# priscilla
# bulent.7474
# hasan.ustun.3762
# 100000143127056
# owen.azubuike
# ickinekin
# aylya99
# lorraine.rain.560
# cherylKikoMimko92
# nglouminati
# zuck
# chan.tat.33
# tkw526
