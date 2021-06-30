import pytest
from modules.reddit import Reddit


@pytest.mark.parametrize("query, post_type", [('Дмитрий Медведев', 'blog'), ('trump', 'url')])
def test_reddit_search(query, post_type):
    obj = Reddit()
    res = obj.search(query, post_type)

    for i in res['data']['results']:

        try:
            assert isinstance(i['likes'], int)
        except AssertionError:
            assert i['likes'] is None

        try:
            assert isinstance(i['datetime'], int)
        except AssertionError:
            assert i['datetime'] is None

        try:
            assert isinstance(i['comments'], int)
        except AssertionError:
            assert i['comments'] is None

        assert i['polarity'] == 'positive' or i['polarity'] == 'negative' or i[
            'polarity'] == 'neutral'

        try:
            assert i['thumbnail'] != ''
            assert isinstance(i['thumbnail'], str)
            assert i['thumbnail'].startswith('http')
        except AssertionError:
            assert i['thumbnail'] is None

        try:
            assert i['url'] != ''
            assert isinstance(i['url'], str)
            assert i['url'].startswith('http')
        except AssertionError:
            assert i['url'] is None

        try:
            assert i['title'] != ''
            assert isinstance(i['title'], str)
        except AssertionError:
            assert i['title'] is None

        try:
            assert i['content'] != ''
            assert isinstance(i['content'], str)
        except AssertionError:
            assert i['content'] is None

        try:
            assert i['category'] != ''
            assert isinstance(i['category'], str)
        except AssertionError:
            assert i['category'] is None

        try:
            assert i['author_userid'] != ''
            assert isinstance(i['author_userid'], str)
            assert ' ' not in i['author_userid']
        except AssertionError:
            assert i['author_userid'] is None

        try:
            assert i['postid'] != ''
            assert isinstance(i['postid'], str)
            assert ' ' not in i['postid']
        except AssertionError:
            assert i['postid'] is None

        try:
            assert i['domain'] != ''
            assert isinstance(i['domain'], str)
            assert ' ' not in i['domain']
        except AssertionError:
            assert i['domain'] is None

        assert i['type'] == 'video' or i['type'] == 'image' or i[
            'type'] == 'link' or i['type'] == 'status'


