"""
    Credentials and Proxy Service Client

    Place this file in your project to access the Credential and Proxy Service, using helper functions.

    get_proxy_random()
    get_credential_random()

    NOTE: Use predefined filter constants wherever provided.

"""
import json
import urllib.request
import urllib.parse
import os
from urllib.error import HTTPError, URLError

""" Constants for filtering purposes """
class ProxyType:
    SOCKS5 = 'socks5'
    HTTPS = 'https'


class ProxyAuth:
    YES = 'yes'
    NO = 'no'


class CredentialType:
    ALL = 'all'
    BASIC_AUTH = 'basic_auth'
    COOKIES = 'cookies'
    API_KEY = 'api_key'


class CredentialPlatform:
    FACEBOOK = 'facebook'
    GOOGLE = 'google'
    INSTAGRAM = 'instagram'
    LINKEDIN = 'linkedin'
    REDDIT = 'reddit'
    TUMBLR = 'tumblr'
    WIKIPEDIA = 'wikipedia'
    YOUTUBE = 'youtube'
    TWITTER = 'twitter'
    SHODAN = 'shodan'
    EMAILCRAWLR = 'emailcrawlr'
    TINEYE = 'tineye'
    MAPBOX = 'mapbox'
    MXTOOLBOX = 'mxtoolbox'
    TWILIO = 'twilio'
    INDICO = 'indico'

""" 
    Custom exception classes for handling HTTPError
    Use these to handle your script when a resource is unavailable
"""
class ProxyNotFoundException(Exception):
    pass


class CredentialNotFoundException(Exception):
    pass


class ServiceUnreachableException(Exception):
    pass


class CapsClient:

    def __init__(self, base_url=None):
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = os.environ.get('CAPS_BASE_URL', 'http://192.168.20.59:5000')
        self.ns_proxy = self.base_url+'/proxy/'
        self.ns_credential = self.base_url+'/credential/'

    """ 
        Get random proxy based on the filters
        Filters:
        country_code - optional - ISOALPHA-2 country codes
        type - optional - listed in class ProxyType
        auth - optional - listed in class ProxyAuth
    """
    def get_proxy_random(self, country_code=None, type=None, auth=None):
        filters = dict()
        params = ''
        if country_code:
            filters['country_code'] = country_code
        if type:
            filters['type'] = type
        if auth:
            filters['auth'] = auth
        if len(filters):
            params = '?'+urllib.parse.urlencode(filters)

        try:
            with urllib.request.urlopen(self.ns_proxy+'random'+params) as f:
                resp = f.read().decode()
            return json.loads(resp)
        except HTTPError as e:
            raise ProxyNotFoundException('Proxy for provided filters doesn\'t exist.')
        except URLError as e:
            raise ServiceUnreachableException('Service is down or you are not connected to the network.')

    """ 
        Get random credential based on the filters
        Filters:
        platform - required - Listed in class CredentialPlatform
        type - optional - Listed in class CredentialType
    """
    def get_credential_random(self, platform, type=CredentialType.ALL):
        params = '?' + urllib.parse.urlencode(dict(platform=platform, type=type))
        try:
            with urllib.request.urlopen(self.ns_credential+'random'+params) as f:
                resp = f.read().decode()
            return json.loads(resp)
        except HTTPError as e:
            raise CredentialNotFoundException('Credential for provided filters doesn\'t exist.')
        except URLError as e:
            raise ServiceUnreachableException('Service is down or you are not connected to the network.')


if __name__ == '__main__':
    o = CapsClient()
    o.get_proxy_random()