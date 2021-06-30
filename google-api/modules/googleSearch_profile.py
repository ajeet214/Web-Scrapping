from urllib.request import Request, urlopen
from bs4 import BeautifulSoup


class ProfileSearch():

    def get(self, query):

        if query.find(' '):
            query = query.replace(' ', '+')
        else:
            pass
        # print(query)

        url = 'https://www.google.com/search?q='+query

        req = Request(url,
                    headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'}
              )
        webpage = urlopen(req).read()
        soup = BeautifulSoup(webpage,'lxml')
        # print(soup)

        info = []
        #---------------------------------------
        page = soup.find('div', id='rhs_block')
        #---------------------------------------

        #image
        image = page.find('a')
        e = image.get('href')
        rest = e.split('&', 1)[0]
        # print(rest)
        img = rest.replace('/imgres?imgurl=','')
        # print(img)

        #image source
        image_link = page.find('img')
        img_link = image_link.get('title')

        #profile_name with designation
        # try:
        #     search = page.find('div', class_='LKVBDc uICYRb')
        #     print('try')
        # except:
        #     search = page.find('div', class_='LKVBDc')
        #     print('except')
        search = page.find('div', class_='LKVBDc')


        #------------------------------
        name = search.find('div', class_='kno-ecr-pt kno-fb-ctx')
        # print(name.text)
        # designation = search.find('div', class_='sthby kno-fb-ctx')
        # print(designation.text)

        #All_about
        des = page.find('div', class_='hb8SAc kno-fb-ctx')
        description = des.find_all('span')
        Text = description[0].text
        # print(Text)
        source_link = description[1].a['href']
        source_name = description[1].text
        # print(source_name,':',source_link)


        #-------------------------
        about = page.find('div', class_="i4J0ge")
        # print(about)
        all_detail=[]
        for mod in about.find_all('div', class_='mod'):

            det = mod.find('div', class_='Z1hOCe')

            if det==None:
                pass
            else:
                g = []
                sd = det
                for i in sd.find_all('span'):

                    f = i.text
                    g.append(f)
                # print(g)

                all_detail.append(g)
        # print(all_detail)
        #--------------------------

        detail = {}
        for q in all_detail:
            # print(q)

            s=(''.join(q)).split(':')
            # print(s)
            detail[s[0]] = s[1]

        # print(detail)
        #-------------------------

        r = page.find('div', {'data-md':'70'})
        pd = {}
        try:
            p = r.find('div', class_='Ss2Faf zbA8Me qLYAZd')
            profile = p.text

            for d in r.find_all('a'):

                pd[d.text] = d['href']

                # print(d.text)
                # print(d['href'])

        except AttributeError:
            pass

        data = {}

        data['image'] = img
        data['image_link'] = img_link
        data['searched_name'] = name.text
        # data['designation'] = designation.text
        data['about'] = Text
        data[source_name] = source_link
        data['Details'] = detail
        data[profile] = pd

        info.append(data)

        return info


if __name__== '__main__':
    obj = ProfileSearch()
    print(obj.get('trump'))
