import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import urllib


#------------------------------------

class ProfileSearch:

    def __init__(self):
        self.proxies = {'https': 'socks5://185.121.139.55:21186'}
        self.headers = {
            'Accept-Language': 'en-US,en;q=0.5',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
                }

    def fb_public_search(self, query):

        query = urllib.parse.quote(query)
        # print(query)

        urls = 'https://www.facebook.com/public/'+query+'?page=1'

        response = requests.get(urls, headers=self.headers, proxies=self.proxies)
        results = []
        soup1 = BeautifulSoup(response.text.replace('<!--', '').replace('-->', ''), "html.parser")
        # print(soup1.prettify())

        # ------------------------------------------------------------
        for item in soup1.find_all('div', class_='_4p2o'):
            sub_data = {}

            try:
                div_1 = item.find('div', class_='clearfix _ikh')
                # print(div_1.find('a', class_='_32mo').text)
                title = div_1.find('a', class_='_32mo')
                verified = title.find('span').span
                if verified is None:
                    sub_data['verified'] = False
                else:
                    sub_data['verified'] = True
            except:
                sub_data['verified'] = False

            # a = item.find('a', class_='_2ial _8o _8s lfloat _ohe')
            image = item.find('img')
            # print(a.img['src'])
            sub_data['image'] = image['src'].replace('amp;', '')

            h = item.find('div', class_='_gll')

            # print(h.a['href'])
            sub_data['url'] = h.a['href']
            sub_data['userid'] = sub_data['url'].split('/')[-1]
            if 'profile.php?id' in sub_data['userid']:
                sub_data['userid'] = sub_data['userid'][15:]
            # print(h.a.text)
            sub_data['name'] = h.a.text
            sub = []

            des1 = item.find('div', class_='_glm')
            # print(des1.text)
            sub.append(des1.text)
            des2 = item.find('div', class_='_glo')
            sub.append(des2.text)
            # print(des2.text)
            # print('\n')
            if des1.text == '' and des2.text == '':
                sub_data['description'] = None
            else:
                sub_data['description'] = ', '.join(str(e) for e in sub)
            # print(sub_data['description'])
            sub_data['type'] = 'identity'
            results.append(sub_data)

        return results


if __name__ == '__main__':
    obj = ProfileSearch()
    print(obj.fb_public_search('mark'))
