import pytest
from modules.googleSearch import GoogleSearch


def Object(query):
    obj = GoogleSearch()
    result = obj.get(query)
    return result


@pytest.mark.parametrize("name", ['andrew', 'Nguyễn'])
def test_normal_search(name):
    result1 = Object(name)
    for i in result1:
        try:
            assert type(i['url']) == str
            assert i['url'].startswith('http')
            assert i['url'] != ""
        except:
            assert i['url'] is None
        try:
            assert i['polarity'] != ""
            assert type(i['polarity']) == str
        except:
            assert i['polarity'] is None

        try:
            assert i['content'] != ""
            assert type(i['content']) == str
        except:
            assert i['content'] is None

        try:
            assert i['title'] != ""
            assert type(i['title']) == str
        except:
            assert i['title'] is None

        try:
            assert i['type'] is 'link' or i['type'] is 'news'
        except:
            assert i['type'] is 'video'






