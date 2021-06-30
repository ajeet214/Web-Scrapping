import requests
from credentials import creds


class Lookups:

    def __init__(self):
        self.key = self._get_key()

    def _get_key(self):
        url = "http://credsnproxy/api/v1/mxtoolbox"
        try:
            cred = requests.get(url=url).json()
            return cred['api_key']
        except:
            return creds['api_key']

    def lookups(self,command,domain):
        headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0'}
        url = 'https://api.mxtoolbox.com/api/v1/Lookup/'+command+'/?argument='+domain+'&Authorization='+self.key
        return requests.get(url=url, headers=headers).json()
    
    
if __name__ == '__main__':
    o = Lookups()
    print(o.lookups('mx','twitter.com'))
