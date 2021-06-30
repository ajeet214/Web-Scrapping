import pytest
from modules.googleNews import GoogleNews


def objects(query):
    obj = GoogleNews()
    result = obj.get(query)
    return result


@pytest.mark.parametrize("name", ['Pedro Sánchez', 'steven paul'])
def test_news_search(name):
    result1 = objects(name)
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
            assert i['source'] != ""
            assert type(i['source']) == str
        except:
            assert i['source'] is None

        try:
            assert i['thumbnail'] != ""
            assert type(i['thumbnail']) == str
        except:
            assert i['thumbnail'] is None

        assert type(i['datetime']) == int

        assert i['type'] is 'news'




