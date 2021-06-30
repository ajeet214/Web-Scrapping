from modules import login_file
from bs4 import BeautifulSoup
from urllib.parse import quote


login = login_file.Login()
login.loginmethod()
client = login.client

url1 = 'https://www.linkedin.com/uas/login'
# print(client.get(url1).text)
soup = BeautifulSoup(client.get(url1).text, 'lxml')
csrf = soup.find('input', {"name": "csrfToken"})['value']
print(csrf)

res = client.get('https://www.linkedin.com/in/petyab/detail/recent-activity')
# print(res.text)
profile_urn = quote(res.text[res.text.find("urn:li:fs_profile:"):res.text.find("urn:li:fs_profile:")+80].split('&')[0])
print(profile_urn)

url = f'https://www.linkedin.com/voyager/api/identity/profileUpdatesV2?count=90&includeLongTermHistory=true&moduleKey=member-activity%3Aphone&profileUrn={profile_urn}&q=memberFeed&start=5'

r = client.get(url, headers={"csrf-token": csrf,
                             "referer": "https://www.linkedin.com/in/petyab/detail/recent-activity/",
                             "x-li-lang": "en_US",
                             "user-agent":  "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
                             "x-li-track": '{"clientVersion":"1.3.3248","osName":"web","timezoneOffset":-7,"deviceFormFactor":"DESKTOP","mpName":"voyager-web"}',
                             "accept-language": 'en-US,en;q=0.9'})

print(r.text)



