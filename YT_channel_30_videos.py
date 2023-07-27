"""
Project : YouTube Channel videos
Author : Ajeet
Date : July 27, 2023
"""

import re
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import json

youtube_search = "https://www.youtube.com/@PW-Foundation/videos"

# Open the URL and read the content of the page
url_search = urlopen(youtube_search)
youtube_page = url_search.read()

# Parse the HTML content of the page using BeautifulSoup
youtube_html = bs(youtube_page, "html.parser")

# # Define a regular expression pattern to extract the JSON data from the script tag
pattern = r'<script nonce="[-\w]+">\n\s+var ytInitialData = (.+)'
script_data = re.search(pattern=pattern, string=youtube_html.prettify())[1].replace(';', '')

# Load the JSON data into a Python dictionary
json_data = json.loads(script_data)

# Extract the list of videos from the JSON data and store it in the 'videos_container' variable
videos_container = json_data['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']['content']['richGridRenderer']['contents']

print(f"Total videos: {len(videos_container)-1}")

# Loop through the video list and print the URLs of the videos
for video in videos_container[:-1]:
    # print(video)
    video_id = video['richItemRenderer']['content']['videoRenderer']['videoId']
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(video_url)


"""
output:

Total videos: 30
https://www.youtube.com/watch?v=LuTONVLzESM
https://www.youtube.com/watch?v=KWXKegvNa-I
https://www.youtube.com/watch?v=dArUpCasmnE
https://www.youtube.com/watch?v=HqG2QchBw8Y
https://www.youtube.com/watch?v=1izKrQHyx9M
https://www.youtube.com/watch?v=jXAb1evxaJc
https://www.youtube.com/watch?v=2dn7XMxRtPE
https://www.youtube.com/watch?v=Fks4dVnTb5M
https://www.youtube.com/watch?v=nIuGXeISbSo
https://www.youtube.com/watch?v=L5G-0FbyAsc
https://www.youtube.com/watch?v=uqDX6hcRf2I
https://www.youtube.com/watch?v=9ZVfDuqKIQM
https://www.youtube.com/watch?v=1wMGzlQTyeM
https://www.youtube.com/watch?v=ivS0xPAbVUs
https://www.youtube.com/watch?v=UJb799ZLCwQ
https://www.youtube.com/watch?v=RPCHRtdO9hg
https://www.youtube.com/watch?v=iN2UWJW3lzo
https://www.youtube.com/watch?v=lRle7Jzciq8
https://www.youtube.com/watch?v=CPmcBN2xoxI
https://www.youtube.com/watch?v=mdZ4g2o7v9g
https://www.youtube.com/watch?v=z3ko4cUOYO0
https://www.youtube.com/watch?v=ZLgLCNKQwFw
https://www.youtube.com/watch?v=J7hFajBOmBo
https://www.youtube.com/watch?v=PXb-jcA2TGA
https://www.youtube.com/watch?v=LxHAzwur8cI
https://www.youtube.com/watch?v=sBXHecS1S1w
https://www.youtube.com/watch?v=l6ZY90YnMy0
https://www.youtube.com/watch?v=33onjejJLDs
https://www.youtube.com/watch?v=o3eOj-jhhfI
https://www.youtube.com/watch?v=ecGcmstmnGA


"""