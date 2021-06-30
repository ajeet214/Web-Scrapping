import requests
from bs4 import BeautifulSoup
import urllib.parse


class PageSearch:

    def __init__(self):

        self.headers = {
            'Accept-Language': 'en-US,en;q=0.5',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }

    def fb_page_search(self, query):

        query = urllib.parse.quote(query)
        count = 0
        results = []

        pages = requests.get('https://www.facebook.com/public?query='+query+'&type=pages', headers=self.headers)
        # print(pages.text)
        soup1 = BeautifulSoup(pages.text, 'html.parser')
        # print(soup1)
        for item in soup1.find_all('code'):
            # print(item)
            soup2 = BeautifulSoup(str(item)[22:-11], "html.parser")
            # print(soup2.prettify())

            for elem in soup2.find_all('div', class_='_1yt'):
                # print(elem)

                for dept in elem.find_all('span', class_='_5bl2'):
                    # print(dept)
                    data = {}

                    # image
                    image = dept.find('img')
                    # print(image.img['src'])
                    data['image'] = image['src']

                    # profile url
                    a = dept.find('a', class_='_32mo')
                    try:
                        temp = a.find('span')
                        verified = temp.find('span')
                        data['verified'] = verified.text
                        data['verified'] = True
                    except:
                        data['verified'] = False
                    # print(a.text)

                    # profile name
                    data['name'] = a.text
                    # print(a['href'])
                    data['url'] = a['href']

                    text = dept.find('div', class_='_glm')
                    # print(text.text)
                    data['description'] = text.text
                    # print('\n\n')
                    # print(data)
                    data['likes'] = None
                    data['category'] = None
                    data['location'] = None
                    data['country'] = None
                    data['country_code'] = None
                    count += 1
                    data['type'] = 'page'
                    results.append(data)

        return results
        # return {'data':
        #         {'results': results,
        #          'total': count}
        #         }


if __name__ == '__main__':
    obj = PageSearch()
    print(obj.fb_page_search('trump'))
