from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from credentials import account_sid, auth_token
from modules.data_gathering import DataSheet


class NumberInfo:

    def __init__(self):

        self.dict = {}
        obj = DataSheet()
        self.country_list = obj.data_extractor()

    def caller_data(self, number):

        client = Client(account_sid, auth_token)

        try:
            phone_number = client.lookups.phone_numbers(number).fetch(type="carrier")
            self.dict['carrier_name'] = phone_number.carrier['name']
            if not self.dict['carrier_name']:
                self.dict['carrier_name'] = None

            self.dict['country_code'] = phone_number.country_code
            if not self.dict['country_code']:
                self.dict['country_code'] = None

            self.dict['national_format'] = phone_number.national_format
            if not self.dict['national_format']:
                self.dict['national_format'] = None

            self.dict['number_type'] = phone_number.carrier['type']
            if not self.dict['number_type']:
                self.dict['number_type'] = None

            self.dict['mobile_country_code'] = phone_number.carrier['mobile_country_code']
            if not self.dict['mobile_country_code']:
                self.dict['mobile_country_code'] = None

            self.dict['mobile_network_code'] = phone_number.carrier['mobile_network_code']
            if not self.dict['mobile_network_code']:
                self.dict['mobile_network_code'] = None

            self.dict['number'] = phone_number.phone_number
            if not self.dict['number']:
                self.dict['number'] = None
            # self.dict['name'] = phone_number.caller_name
            # print(phone_number.caller_name)
            for i in self.country_list:
                dict2 = {}
                if self.dict['country_code'] == i['country']:
                    self.dict['country'] = i['name']
                    dict2['latitude'] = i['latitude']
                    dict2['longitude'] = i['longitude']
                    self.dict['geo_location'] = dict2
            # print(phone_number.carrier)
            return self.dict

        except TwilioRestException:
            self.dict['number'] = 'invalid'
            return self.dict


if __name__ == '__main__':
    obj = NumberInfo()
    print(obj.caller_data("+79146729573"))
