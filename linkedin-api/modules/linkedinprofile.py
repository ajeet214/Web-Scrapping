import sys
import json

from modules import login_file, dataprocessor
import pymongo
# config file
from bs4 import BeautifulSoup


def StatusCreator(dictdata):
    status = True
    try:
        value =0
        for i in dictdata.keys():
            if len(dictdata[i]) == 0 and str(i) not in "summary":
                value+=1
            elif str(i)  in "summary":
                if dictdata[i]["image"] is None:
                    value+=1
        if value == 9:
            raise Exception
    except:
        status = False
    finally:
        return status


class ProfileFetcher():

    def __init__(self):
        try:
            login = login_file.Login()
            login.loginmethod()
            self._browser = login.client
        except:
            print("error>>init::",sys.exc_info()[1])

    def Porfile(self, username):
        url = 'https://www.linkedin.com/in/' + username
        # url=urllib.parse.unquote_plus(url)
        print(url)
        data = {}
        try:
            k = self._browser.get(url)
            html = str(k.content.decode())
            html = html.replace("&#92;&quot;", "'")
            html = html.replace("&quot;", '"')
            html = html.replace("&amp;", '&')
            html = html.replace("&#61;", "=")
            html = html.replace("&gt;", ">")
            html = html.replace("\\n", "")
            soup = BeautifulSoup(html,"lxml")
            # print(soup.prettify())
            divdata = soup.findAll("code",{"style":"display: none"})
            k = 0
            mainstr = ''

            for i in divdata:
                temp = str(i.text)
                if k< len(temp):
                    k = len(temp)
                    mainstr = temp
            # print(str(mainstr))
            # print(json.loads(mainstr))
            profilep = dataprocessor.Decomposer(d=str(mainstr))
            data = profilep.startfunc()
            # self._collection.insert(data.copy())
            # this function will check values in data dict and send status
            data["status"] = StatusCreator(data.copy())
            data["profile_url"] = url
            json_data = json.loads(mainstr)
            # print(json_data['included'])
            image = ''
            for i in json_data['included']:
                try:
                    image = i['picture']['rootUrl']+i['picture']['artifacts'][-1]['fileIdentifyingUrlPathSegment']

                except:
                    pass

            data['summary']['image'] = image

        except:
            data["status"] = False
            print("error>>profile::", sys.exc_info()[1])
        finally:
            return data


if __name__ == '__main__':
    k = ProfileFetcher()
    # url = urllib.parse.quote_plus("https://www.linkedin.com/in/xuefenghere/")
    # print(url)
    print(k.Porfile('williamhgates'))

# markaweinberger
# xuefenghere