from urllib.parse import urlencode
import pymongo
import json
from bs4 import BeautifulSoup
import demjson
import redis
import multiprocessing
from time import sleep
# config file
from config import Config
from requests_futures.sessions import FuturesSession
from concurrent.futures import ThreadPoolExecutor
from credentials import creds
from modules import login_file
from modules import minio_push


class ProfileSearch:

    def __init__(self):
        self.session = FuturesSession(executor=ThreadPoolExecutor(max_workers=5))

        mon = pymongo.MongoClient(host=login_file.host, port=login_file.port)
        db = mon[login_file.db]
        self.collection = db[login_file.collection_search]

    def redis_channel(self, selenium_session):

        # r = redis.Redis(host=self.redis_host, port=self.redis_port)
        r = redis.from_url("redis://" + Config.REDIS_URI)
        client_id = 'linkedin_profile_search' + selenium_session
        p = r.pubsub()  # pubsub object
        p.subscribe(client_id)
        return client_id, r, p

    # -----------------------------------------------------------------------------

    def _dicteditor(self, data, client_id, redis_obj, channel_obj):

        data = data.encode('latin1').decode('utf8')
        # print(data)
        soup = BeautifulSoup(data, 'lxml')

        # print(soup)
        data_ = demjson.decode([each_code.text for each_code in soup.find_all('code')][-3])
        try:
            total_res = data_['data']['metadata']['totalResultCount']

            print(total_res)

            # print(soup)
            self.lst = []

            for each_code in soup.find_all('code'):
                # lst.append(each_code.text)
                self.lst.append(each_code.text)
            # print(self.lst[-3])
            data = demjson.decode(self.lst[-3])
            # print(data)
            data1 = data['data']['elements']
            # print('data1', data1)
            self.temp_lst2 = []

            for i in data1:

                if i['type'] == 'SEARCH_HITS':

                    for j in i['elements']:
                        temp_dct2 = dict()

                        # for non linkedin members
                        try:
                            temp_dct2['userid'] = j['publicIdentifier']
                            temp_dct2['location'] = j['subline']['text']
                            temp_dct2['full_name'] = j['title']['text']
                            self.temp_lst2.append(temp_dct2)

                        # if linkedin member then pass
                        except KeyError:
                            pass
                else:
                    pass
                # try:
                #     if len(i['elements']) == 0:
                #         pass
                #     else:
                #         # print(len(i['elements']))
                #         for j in i['elements']:
                #             temp_dct2 = {}
                #             temp_dct2['location'] = j['subline']['text']
                #             temp_dct2['userid'] = j['publicIdentifier']
                #             temp_dct2['full_name'] = j['title']['text']
                #             self.temp_lst2.append(temp_dct2)
                # except KeyError:
                #     pass

            # print('fullname,location,userid\n', self.temp_lst2)
            data2 = data['included']
            # print(data2)
            # print(demjson.encode(data2))
            self.lst1 = []

            # ---------------------------------
            for dct in data2:
                # print(dct,'\n')
                if "firstName" in dct:
                    if dct['firstName'] == "":
                        pass
                    # print(dct['entityUrn'][22:])
                    else:
                        self.lst1.append(dct)

            # print('firstname,lastname ...\n', self.lst1)
            self.temp_lst1 = []

            for i in self.lst1:
                temp_dct = {}
                # temp_dct['firstName'] = i['firstName']
                # temp_dct['lastName'] = i['lastName']
                temp_dct['userid'] = i['publicIdentifier']
                temp_dct['url'] = "https://www.linkedin.com/in/"+i['publicIdentifier']
                try:
                    temp_dct['description'] = i['occupation']
                except:
                    pass
                try:
                    temp_dct['image'] = i['picture']['rootUrl']+i['picture']['artifacts'][-1]['fileIdentifyingUrlPathSegment']
                except:
                    temp_dct['image'] = None

                self.temp_lst1.append(temp_dct)
            # print("url,userid,image&des\n", self.temp_lst1)
            self.location_list = []

            #---------------------------------
            for x in self.temp_lst1:
                for y in self.temp_lst2:

                    if y['userid'] == x['userid']:
                        x['location'] = y['location']
                        self.location_list.append(x['location'])
                        x['name'] = y['full_name']

            # print('locations\n', self.location_list)

            rs = []
            for u in self.location_list:
                rs.append(self.session.get('https://maps.google.com/maps/api/geocode/json?address=' + str(
                    u) + '&key='+creds['google_key']))
            results = []
            for response in rs:
                temp_dict = {}
                r = response.result()
                lt = demjson.decode(r.content.decode('utf-8'))
                # print(lt)
                # print(lt['results'][0]['address_components'])
                try:
                    for i in lt['results'][0]['address_components']:
                        if i['types'][0] == 'country':
                            # print(i['long_name'])
                            temp_dict['country_code'] = i['short_name']
                            temp_dict['country'] = i['long_name']
                            results.append(temp_dict)
                except:
                    temp_dict['country_code'] = None
                    temp_dict['country'] = None
                    results.append(temp_dict)
            #
            # print(results)
            # print(self.temp_lst1)
            final_list = []
            print('@@@', len(self.temp_lst1))
            for i in range(len(self.temp_lst1)):
                final_dict = {}
                try:
                    final_dict['location'] = self.temp_lst1[i]['location']
                except:
                    final_dict['location'] = None

                try:
                    if self.temp_lst1[i]['location'] is None:
                        final_dict['country_code'] = None
                        final_dict['country'] = None
                    else:
                        final_dict['country_code'] = results[i]['country_code']
                        final_dict['country'] = results[i]['country']
                except IndexError:
                    final_dict['country_code'] = None
                    final_dict['country'] = None

                final_dict['url'] = self.temp_lst1[i]['url']
                final_dict['userid'] = self.temp_lst1[i]['userid']

                # try:
                #     final_dict['image'] = self.temp_lst1[i]['image']
                # except:
                #     final_dict['image'] = None
                final_dict['name'] = self.temp_lst1[i]['name']
                final_dict['description'] = self.temp_lst1[i]['description']

                try:
                    image_url = self.temp_lst1[i]['image']
                    minio_url = minio_push.start_uploading([image_url], 'linkedin-service')
                    for i in minio_url:
                        if i['status'] == 200:
                            final_dict['image'] = i['file_url']
                        else:
                            raise Exception('image not found')
                except:
                    final_dict['image'] = None


                # type is by default identity
                final_dict['type'] = 'identity'
                final_list.append(final_dict)
                redis_obj.publish(client_id, json.dumps(final_dict))
                print(final_dict)
            # return final_list
            return total_res
            # return self.temp_lst1
        except KeyError as e:
            print(e)
            return 'ERROR'

    def pagination(self, first_page_url, client_id, redis_obj, channel_obj):

        condition = True
        page_number = 1
        c = 1

        while condition:

            if page_number == 1:
                k = self.client.get(first_page_url)
                total = self._dicteditor(k.text, client_id, redis_obj, channel_obj)
                if total == 'ERROR':
                    condition = False
                    redis_obj.publish(client_id, 'EOF')
                    channel_obj.unsubscribe(client_id)

            else:
                print('************')
                k = self.client.get(f'{first_page_url}&page={page_number}')
                total = self._dicteditor(k.text, client_id, redis_obj, channel_obj)
            # print(k.text)
            print(total, type(total))
            page_number += 1

            try:
                number_of_total_pages = int(total / 10)

                # print(number_of_total_pages)
                if number_of_total_pages < 20:

                    if number_of_total_pages <= 1:
                        condition = False
                        redis_obj.publish(client_id, 'EOF')
                        channel_obj.unsubscribe(client_id)
                    pass
            except TypeError as e:
                print(e)
                condition = False
                redis_obj.publish(client_id, 'EOF')
                channel_obj.unsubscribe(client_id)

            if c == 20:
                condition = False
                redis_obj.publish(client_id, 'EOF')
                channel_obj.unsubscribe(client_id)
            c += 1
            sleep(2)

    # ----------------------------------------------------------------
    def search(self, q=None, company=None, region=None, language=None, title=None):

        base_url = "https://www.linkedin.com/search/results/people/?"

        url = ''

        if q and company and region and language and title:
            url = f'{base_url}company={company}&facetGeoRegion=%5B"{region}%3A0"%5D&facetProfileLanguage=%5B"{language}"%5D&keywords={q}&origin=FACETED_SEARCH&title={title}'

        # combination of 4 ----------------------------------------
        elif q and company and region and language:
            url = f'{base_url}company={company}&facetGeoRegion=%5B"{region}%3A0"%5D&facetProfileLanguage=%5B"{language}"%5D&keywords={q}&origin=FACETED_SEARCH'

        elif q and company and region and title:
            url = f'{base_url}company={company}&facetGeoRegion=%5B"{region}%3A0"%5D&keywords={q}&origin=FACETED_SEARCH&title={title}'

        elif q and company and language and title:
            url = f'{base_url}company={company}&facetProfileLanguage=%5B"{language}"%5D&keywords={q}&origin=FACETED_SEARCH&title={title}'

        elif q and region and language and title:
            url = f'{base_url}&facetGeoRegion=%5B"{region}%3A0"%5D&facetProfileLanguage=%5B"{language}"%5D&keywords={q}&origin=FACETED_SEARCH&title={title}'

        elif company and region and language and title:
            url = f'{base_url}company={company}&facetGeoRegion=%5B"{region}%3A0"%5D&facetProfileLanguage=%5B"{language}"%5D&origin=FACETED_SEARCH&title={title}'


        # combination of 3 -----------------------------------------
        elif q and company and region:
            url = f'{base_url}company={company}&facetGeoRegion=%5B"{region}%3A0"%5D&keywords={q}&origin=FACETED_SEARCH'

        elif q and company and title:
            url = f'{base_url}company={company}&keywords={q}&origin=FACETED_SEARCH&title={title}'

        elif q and company and language:
            url = f'{base_url}company={company}&facetProfileLanguage=%5B"{language}"%5D&keywords={q}&origin=FACETED_SEARCH'

        elif q and region and language:
            url = f'{base_url}facetGeoRegion=%5B"{region}%3A0"%5D&facetProfileLanguage=%5B"{language}"%5D&keywords={q}&origin=FACETED_SEARCH'

        elif q and region and title:
            url = f'{base_url}facetGeoRegion=%5B"{region}%3A0"%5D&keywords={q}&origin=FACETED_SEARCH&title={title}'

        elif q and title and language:
            url = f'{base_url}facetProfileLanguage=%5B"{language}"%5D&keywords={q}&origin=FACETED_SEARCH&title={title}'

        elif region and title and language:
            url = f'{base_url}facetGeoRegion=%5B"{region}%3A0"%5D&facetProfileLanguage=%5B"{language}"%5D&origin=FACETED_SEARCH&title={title}'

        elif company and region and title:
            url = f'{base_url}company={company}&facetGeoRegion=%5B"{region}%3A0"%5D&origin=FACETED_SEARCH&title={title}'

        elif company and region and language:
            url = f'{base_url}company={company}&facetGeoRegion=%5B"{region}%3A0"%5D&facetProfileLanguage=%5B"{language}"%5D&origin=FACETED_SEARCH'

        elif company and title and language:
            url = f'{base_url}company={company}&facetProfileLanguage=%5B"{language}"%5D&origin=FACETED_SEARCH&title={title}'

        # combination of 2 -----------------------------------------
        elif q and company:
            url = f'{base_url}company={company}&keywords={q}&origin=FACETED_SEARCH'

        elif q and region:
            url = f'{base_url}facetGeoRegion=%5B"{region}%3A0"%5D&keywords={q}&origin=FACETED_SEARCH'

        elif q and title:
            url = f'{base_url}keywords={q}&origin=FACETED_SEARCH&title={title}'

        elif q and language:
            url = f'{base_url}facetProfileLanguage=%5B"{language}"%5D&keywords={q}&origin=FACETED_SEARCH'

        elif company and region:
            url = f'{base_url}company={company}&facetGeoRegion=%5B"{region}%3A0"%5D&origin=FACETED_SEARCH'

        elif company and title:
            url = f'{base_url}company={company}&origin=FACETED_SEARCH&title={title}'

        elif company and language:
            url = f'{base_url}company={company}&facetProfileLanguage=%5B"{language}"%5D&origin=FACETED_SEARCH'

        elif region and title:
            url = f'{base_url}facetGeoRegion=%5B"{region}%3A0"%5D&origin=FACETED_SEARCH&title={title}'

        elif region and language:
            url = f'{base_url}facetGeoRegion=%5B"{region}%3A0"%5D&facetProfileLanguage=%5B"{language}"%5D&origin=FACETED_SEARCH'

        elif title and language:
            url = f'{base_url}facetProfileLanguage=%5B"{language}"%5D&origin=FACETED_SEARCH&title={title}'

        # combination of 1 -----------------------------------------
        elif q:
            url = f'{base_url}keywords={q}&origin=FACETED_SEARCH'

        elif company:
            url = f'{base_url}company={company}&origin=FACETED_SEARCH'

        elif region:
            url = f'{base_url}facetGeoRegion=%5B"{region}%3A0"%5D&origin=FACETED_SEARCH'

        elif title:
            url = f'{base_url}origin=FACETED_SEARCH&title={title}'

        elif language:
            url = f'{base_url}facetProfileLanguage=%5B"{language}"%5D&origin=FACETED_SEARCH'
        # ----------------------------------------------------------

        f_url = url.replace(' ', '%20')

        login = login_file.Login()
        login.loginmethod()
        self.client = login.client

        k = self.client.get(f_url)
        soup1 = BeautifulSoup(k.text, 'lxml')
        # print(soup1.prettify())

        data = demjson.decode([each_code.text for each_code in soup1.find_all('code')][-3])
        print(data)
        try:
            total_res = data['data']['metadata']['totalResultCount']
            print(total_res)
            if total_res == 0:
                return {"message": "no data found"}

            session_id = str(self.client).replace('<requests.sessions.Session object at ', '')
            client_id, redis_obj, channel_obj = self.redis_channel(session_id)
            t = multiprocessing.Process(target=self.pagination,
                                        args=(f_url, client_id, redis_obj, channel_obj))
            t.start()

            return {"channel_id": client_id}

        except KeyError:
            return {"message": "no data found"}


if __name__ == '__main__':

    obj = ProfileSearch()
    # print(obj.search(q="justin", language='en', region='us', company='google', title='software engineer'))
    print(obj.search(q="joe patrick", company='berkshire hathaway', title='assistant'))

# Juha Sipilä
# Владимир Путин
# Nguyễn Xuân Phúc