from modules import login_file
from bs4 import BeautifulSoup
import json


class UserInterests:

    def __init__(self):

        login = login_file.Login()
        login.loginmethod()
        self.client = login.client

    def group_data(self, each_item):
        group_member_list = each_item[0:len(each_item) // 2]
        group_detail_list = each_item[len(each_item) // 2:]
        group = list()

        for i in group_detail_list:
            for j in group_member_list:
                if i['objectUrn'] in j['entityUrn']:
                    i['group_members'] = j['followerCount']

            group.append(i)

        for i in group:
            i['group_name'] = i['groupName']
            i['group_description'] = i['groupDescription']

            if i['logo']:
                i['group_image'] = i['logo']['rootUrl'] + str(
                    [n['fileIdentifyingUrlPathSegment'] for n in i['logo']['artifacts'] if
                     n['width'] == 92]).replace('[', '').replace("'", '').replace(']', '')
            else:
                i['group_image'] = None

            i.pop('groupName')
            i['group_url'] = 'https://www.linkedin.com/groups/'+i['objectUrn'].replace('urn:li:group:', '')
            i.pop('groupDescription')
            i.pop('entityUrn')
            i.pop('recentActivityCount')
            i.pop('logo')
            i.pop('trackingId')
            i.pop('$type')
            i.pop('objectUrn')

        # print(group)
        return group

    def school_data(self, each_item):
        school_followers_list = each_item[0:len(each_item) // 2]
        school_detail_list = each_item[len(each_item) // 2:]
        school = list()

        for i in school_detail_list:
            for j in school_followers_list:
                if i['objectUrn'] in j['entityUrn']:
                    i['followers'] = j['followerCount']

            school.append(i)

        for i in school:
            i['school_name'] = i['schoolName']

            if i['logo']:
                i['school_image'] = i['logo']['rootUrl'] + str(
                    [n['fileIdentifyingUrlPathSegment'] for n in i['logo']['artifacts'] if
                     n['width'] == 400]).replace('[', '').replace("'", '').replace(']', '')
            else:
                i['school_image'] = None

            i.pop('schoolName')
            i.pop('entityUrn')
            i.pop('active')
            i.pop('logo')
            i.pop('trackingId')
            i.pop('$type')

        # print(school)
        return school

    def company_data(self, each_item):
        company_followers_list = each_item[0:len(each_item) // 2]
        company_detail_list = each_item[len(each_item) // 2:]
        company = list()

        for i in company_detail_list:
            for j in company_followers_list:
                if i['objectUrn'] in j['entityUrn']:
                    i['followers'] = j['followerCount']

            company.append(i)

        for i in company:
            i['company_name'] = i['name']

            if i['logo']:
                i['company_image'] = i['logo']['rootUrl'] + str(
                    [n['fileIdentifyingUrlPathSegment'] for n in i['logo']['artifacts'] if
                     n['width'] == 400]).replace('[', '').replace("'", '').replace(']', '')
            else:
                i['company_image'] = None

            i['company  _url'] = 'https://www.linkedin.com/company/' + i['objectUrn'].replace('urn:li:company:', '')
            i.pop('name')
            i.pop('entityUrn')
            i.pop('objectUrn')
            i.pop('active')
            i.pop('logo')
            i.pop('showcase')
            i.pop('universalName')
            i.pop('trackingId')
            i.pop('$type')

        # print(company)
        return company

    def influencers_data(self, each_item):
        influencer_followers_list = each_item[0:len(each_item) // 2]
        influencer_detail_list = each_item[len(each_item) // 2:]
        influencers = list()

        for i in influencer_detail_list:
            for j in influencer_followers_list:
                if i['objectUrn'] in j['entityUrn']:
                    i['followers'] = j['followerCount']

            influencers.append(i)

        for i in influencers:
            i['name'] = f'{i["firstName"]} {i["lastName"]}'
            i['occupation'] = i['occupation']
            i['username'] = i['publicIdentifier']

            if i['picture']:
                i['image'] = i['picture']['rootUrl'] + str(
                    [n['fileIdentifyingUrlPathSegment'] for n in i['picture']['artifacts'] if
                     n['width'] == 800]).replace('[', '').replace("'", '').replace(']', '')
            else:
                i['image'] = None

            i['company  _url'] = 'https://www.linkedin.com/in/'+i['username']
            i.pop('firstName')
            i.pop('lastName')
            i.pop('objectUrn')
            i.pop('entityUrn')
            i.pop('backgroundImage')
            i.pop('publicIdentifier')
            i.pop('picture')
            i.pop('trackingId')
            i.pop('$type')

        # print(influencers)
        return influencers

    def process_influencer(self, temp_list):
        # print(len(temp_list))
        if len(temp_list) <= 1:
            return {"message": "no influencer found"}
        else:
            # print(max(temp_list, key=len))
            return self.influencers_data(max(temp_list, key=len))

    def data_processing(self, soup1, category):

        all_data = list()
        for each_code in soup1.find_all('code'):

            try:
                all_json = json.loads(each_code.text)
                try:
                    # data = all_json['data']
                    data = all_json['included']
                    # print(data)
                    if data:
                        all_data.append(data)

                # filterout those json which don't have 'data' field
                except KeyError:
                    pass

            # # to filter out the non json data
            except json.decoder.JSONDecodeError:
                pass

        # print(all_data)
        temp_list = list()
        for each_item in all_data:
            # print(each_item)

            if category == 'groups':
                if any("urn:li:fs_followingInfo:urn:li:group:" in x['entityUrn'] for x in each_item):
                    return self.group_data(each_item)

            elif category == 'schools':
                if any('urn:li:fs_followingInfo:urn:li:school:' in x['entityUrn'] for x in each_item):
                    return self.school_data(each_item)

            elif category == 'companies':
                if any('urn:li:fs_followingInfo:urn:li:company:' in x['entityUrn'] for x in each_item):
                    return self.company_data(each_item)

            elif category == 'influencers':

                if any('urn:li:fs_followingInfo:urn:li:member:' in x['entityUrn'] for x in each_item):
                    temp_list.append(each_item)
                    return self.process_influencer(temp_list)

    def user_interests(self, username=None, category=None):

        url = f'https://www.linkedin.com/in/{username}/detail/interests/influencers'
        print(url)

        response = self.client.get(url)

        soup1 = BeautifulSoup(response.text, 'lxml')
        # print(soup1.prettify())

        if self.data_processing(soup1, category):
            return self.data_processing(soup1, category)
        else:
            return {"message": f'no {category} found'}


if __name__ == '__main__':

    Obj = UserInterests()
    '''possible category options:
        influencers
        companies
        groups
        schools
    '''
    print(Obj.user_interests(username='reidhoffman', category='companies'))


# test_samples
# petyab
# victorriparbelli
# rumyana-vaseva
# no group/influencer :  oliviarosegliesewinkel
# reidhoffman
