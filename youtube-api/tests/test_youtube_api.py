from modules.youtube_api import YoutubeApi
import pytest


@pytest.mark.parametrize('query', ['romen reign', 'tim cook'])
def test_youtube_search(query):
    obj = YoutubeApi()
    res = obj.searchApi(query)

    for i in res['data']['results']:

        assert isinstance(i['datetime'], int)

        try:
            assert isinstance(i['content'], str)
            assert i['content'] is not ''
        except AssertionError:
            assert i['content'] is None

        try:
            assert isinstance(i['title'], str)
            assert i['title'] is not ''
        except AssertionError:
            assert i['title'] is None

        try:
            assert isinstance(i['author_userid'], str)
            assert i['author_userid'] is not ''
            assert ' ' not in i['author_userid']
        except AssertionError:
            assert i['author_userid'] is None

        try:
            assert isinstance(i['postid'], str)
            assert i['postid'] is not ''
            assert ' ' not in i['postid']
        except AssertionError:
            assert i['postid'] is None

        try:
            assert isinstance(i['author_name'], str)
            assert i['author_name'] is not ''
        except AssertionError:
            assert i['author_name'] is None

        try:
            assert isinstance(i['thumbnail'], str)
            assert i['thumbnail'] is not ''
            assert i['thumbnail'].startswith('http')
        except AssertionError:
            assert i['thumbnail'] is None

        try:
            assert isinstance(i['author_url'], str)
            assert i['author_url'] is not ''
            assert i['author_url'].startswith('http')
        except AssertionError:
            assert i['author_url'] is None

        try:
            assert isinstance(i['url'], str)
            assert i['url'] is not ''
            assert i['url'].startswith('http')
        except AssertionError:
            assert i['url'] is None

        assert i['polarity'] is 'neutral' or 'positive' or 'negative'

        try:
            assert i['type'] is 'page'
        except AssertionError:
            assert i['type'] is 'video'
