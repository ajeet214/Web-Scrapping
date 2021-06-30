import json
import requests
from modules.sentiment import SentimentAnalysis


class Reddit:

    def __init__(self):

        self.proxy = self._get_proxy()
        self.obj = SentimentAnalysis()
        self.neg_count = 0
        self.neu_count = 0
        self.pos_count = 0
        self.domain = "https://www.reddit.com"
        self.url = self.domain + "/search/.json?q={0}&restrict_sr=&sort=relevance&t=all&limit=100"
        self.urls = {
            "blog": self.url,
            "subblog": self.url.format("subreddit:{0}"),
            "username":  self.url.format("author:{0}"),
            "site":  self.url.format("site:{0}"),
            "url":  self.url.format("url:{0}"),
            "selftext":  self.url.format("selftext:{0}"),
        }

    def _get_proxy(self):
        url = "http://credsnproxy/api/v1/proxy"
        try:
            req = requests.get(url=url)
            if req.status_code != 200:
                raise ValueError
            return req.json()
        except:
            return {"proxy_host": '103.59.95.71',
                    "proxy_port": '23344'}

    def search(self, query, stype):
        if stype not in self.urls:
            raise Exception("Reddit Api Module: unknow search type is send")

        request_url = self.urls[stype].format(query)
        # print(request_url)
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0'
        }
        req = requests.get(url=request_url, headers=headers, proxies={
            "http": "socks5://"+self.proxy['proxy_host']+':'+self.proxy['proxy_port']}).text
        response = json.loads(req)
        # print(response)
        if stype == 'username' or stype == 'url' or stype == 'site':
            stype_db = 'blog'
        else:
            stype_db = stype
        data = dict()
        data['results'] = self.insert_raw_json(json.dumps(response), stype=stype_db)

        # return data
        ps = self.pos_count
        ng = self.neg_count
        nu = self.neu_count
        total = ps + ng + nu

        sentiments = dict()
        sentiments["positive"] = ps
        sentiments["negative"] = ng
        sentiments["neutral"] = nu

        data['sentiments'] = sentiments
        data['total'] = total

        return {'data': data
                }

    def insert_raw_json(self, data, stype=None):
        data = json.loads(data)
        # print(data)
        if stype is None:
            raise Exception("search_type cannot be none")

        elif stype == "blog":
            count = 0
            posts = []

            for dat in data['data']['children']:
                posts += [self.insert_data(dat)]

                count += 1
            return posts

        elif stype == 'post':
            posts = []

            for dat in data:

                for da in dat['data']['children']:
                    posts += [self.insert_data(da)]

            return posts

    def insert_data(self, data):

        if data['kind'] == 't3':
            # print(data['data'])
            post = dict()
            post['datetime'] = int(data["data"]["created"])
            if not post['datetime']:
                post['datetime'] = None

            post['author_userid'] = data["data"]["author"]
            post['url'] = data['data']['url']
            post['title'] = data['data']['title']
            post['content'] = data['data']['selftext']
            if not post['content']:
                post['content'] = None

            post['postid'] = data['data']['id']
            post['likes'] = data['data']['ups']
            if not post['likes']:
                post['likes'] = None

            try:
                # check the type of post
                post['type'] = data['data']['post_hint']
                if ':video' in post['type']:
                    post['type'] = 'video'
                elif post['type'] == 'link':
                    post['type'] = 'link'
                elif post['type'] == 'image':
                    post['type'] = 'image'
                elif post['type'] == 'self':
                    post['type'] = 'status'

            except:
                post['type'] = 'status'


            # post['clicked'] = data['data']['clicked']
            # post['score'] = data['data']['score']
            post['category'] = data['data']['subreddit_name_prefixed'][2:]
            post['domain'] = data['data']['domain']
            # post['hidden'] = data['data']['hidden']
            post['comments'] = data['data']['num_comments']
            if not post['comments']:
                post['comments'] = None

            post['thumbnail'] = data['data']['thumbnail']
            if post['thumbnail'] == 'self':
                post['thumbnail'] = None
            elif post['thumbnail'] == 'default':
                post['thumbnail'] = None
            # post['subreddit_id'] = data['data']['subreddit_id']
            pol = self.obj.analize_sentiment(data['data']['title'])
            post['polarity'] = pol

            if pol == 1:
                post['polarity'] = 'positive'
                self.pos_count += 1
            elif pol == -1:
                post['polarity'] = 'negative'
                self.neg_count += 1
            else:
                post['polarity'] = 'neutral'
                self.neu_count += 1

            return post


if __name__ == "__main__":

    reddit = Reddit()
    # print(reddit.search('Дмитрий Медведев', "blog"))
    print(reddit.search('katty', "blog"))
