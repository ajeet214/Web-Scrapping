import pytest
from modules.wikileaks import Wikileaks


@pytest.mark.parametrize("query", ['nasa', 'emmanuel macron'])
def test_wikileaks(query):
    obj = Wikileaks()
    res = obj.wikileaks(query)

    for i in res['data']:

        try:
            assert isinstance(i['title'], str)
            assert i['title'] is not ''
        except:
            assert i['title'] is None

        try:
            assert isinstance(i['author_name'], str)
            assert i['author_name'] is not ''
        except:
            assert i['author_name'] is None

        try:
            assert isinstance(i['content'], str)
            assert i['content'] is not ''
        except:
            assert i['content'] is None

        try:
            assert isinstance(i['url'], str)
            assert i['url'] is not ''
            assert i['url'].startswith('http')
        except:
            assert i['url'] is None

        try:
            assert isinstance(i['author_image'], str)
            assert i['author_image'] is not ''
            assert i['author_image'].startswith('http')
        except:
            assert i['author_image'] is None

        try:
            assert isinstance(i['datetime'], int)
        except:
            assert i['datetime'] is None

        try:
            assert i['type'] is 'link'
        except:
            assert i['type'] is 'document'
