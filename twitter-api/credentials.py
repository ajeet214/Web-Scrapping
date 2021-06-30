import requests
google_keys = 'AIzaSyASmizHZrRrEU6tJH0XgP3QXNae7CMEEW4'

class TwitterKeys:

    def __init__(self):

        cred = self._get_credentials()
        self.consumer_key = cred['consumer_key']
        self.consumer_secret = cred['consumer_secret']
        self.access_token = cred['access_token']
        self.access_token_secret = cred['access_token_secret']

    def _get_credentials(self):
        # change url as per credentials reequired
        url = "http://credsnproxy/api/v1/twitter"
        try:
            req = requests.get(url=url)
            if req.status_code != 200:
                raise ValueError
            return req.json()
        except:
            # return fallback object
            return {
                'consumer_key': 'JTZXO4ZIyBpUutRtZ5UeFaJ09',
                'consumer_secret': 'SjyeEiNefvGZjxcQ7IZIcb1La0LEnOQDkwCIZxPeQf7KNdxTjf',
                'access_token': '961409682639376385-2CilwrmHqL9Gaox3ul4S1H4mIms1jeG',
                'access_token_secret': 'yhA4oD03nLOBCklwUbLsyOzT4tst1SHXBq269a7aYp9kX'
            }
