import pytest
from modules.linkedinSearch import SearchClass


@pytest.mark.parametrize("query",["bill gates", "Владимир Путин"])
def test_linkedinSearch(query):
    obj = SearchClass()
    res = obj.search(query)

    for i in res['results']:

        try:
            assert isinstance(i['location'], str)
            assert i['location'] is not ''
        except:
            assert i['location'] is None

        try:
            assert isinstance(i['country'], str)
            assert i['country'] is not ''
        except:
            assert i['country'] is None

        try:
            assert isinstance(i['description'], str)
            assert i['description'] is not ''
        except:
            assert i['description'] is None

        try:
            assert isinstance(i['userid'], str)
            assert i['userid'] is not ''
            assert ' ' not in i['userid']
        except:
            assert i['userid'] is None

        try:
            assert isinstance(i['name'], str)
            assert i['name'] is not ''
        except:
            assert i['name'] is None

        try:
            assert isinstance(i['country_code'], str)
            assert i['country_code'] is not ''
            assert len(i['country_code']) is 2
        except:
            assert i['country_code'] is None

        try:
            assert isinstance(i['image'], str)
            assert i['image'] is not ''
            assert i['image'].startswith('http')
        except:
            assert i['image'] is None

        try:
            assert isinstance(i['url'], str)
            assert i['url'] is not ''
            assert i['url'].startswith('http')
        except:
            assert i['url'] is None

        assert i['type'] is 'identity'

