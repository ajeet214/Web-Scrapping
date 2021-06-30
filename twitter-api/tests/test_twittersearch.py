import pytest
from modules.twitter_profile_search import TwitterSearch


def search(query):
    obj = TwitterSearch()
    return obj.profilesearch(query)


@pytest.mark.parametrize("query", ['bill gates', 'Nguyễn Xuân Phúc'])
def test_twitter_search(query):
    res = search(query)

    for i in res:
        assert isinstance(i['posts'], int)
        assert isinstance(i['datetime'], int)
        assert isinstance(i['likes'], int)
        assert isinstance(i['followers'], int)
        assert isinstance(i['following'], int)
        assert type(i['verified']) == bool

        try:
            assert isinstance(i['name'], str)
            assert i['name'] != ""
        except AssertionError:
            assert i['name'] is None

        try:
            assert isinstance(i['location'], str)
            assert i['location'] != ""
        except AssertionError:
            assert i['location'] is None

        try:
            assert isinstance(i['description'], str)
            assert i['description'] != ""
        except AssertionError:
            assert i['description'] is None

        try:
            assert isinstance(i['country'], str)
            assert i['country'] != ""
        except AssertionError:
            assert i['country'] is None

        try:
            assert isinstance(i['polarity'], str)
            assert i['polarity'] != ""
        except AssertionError:
            assert i['polarity'] is None

        try:
            assert isinstance(i['userid'], str)
            assert i['userid'] != ""
        except AssertionError:
            assert i['userid'] is None

        try:
            assert isinstance(i['url'], str)
            assert i['url'] != ""
            assert i['url'].startswith('http')
        except AssertionError:
            assert i['url'] is None

        try:
            assert isinstance(i['linked_url'], str)
            assert i['linked_url'] != ""
            assert i['linked_url'].startswith('http')
        except AssertionError:
            assert i['linked_url'] is None

        try:
            assert isinstance(i['image'], str)
            assert i['image'] != ""
            assert i['image'].startswith('http')
        except AssertionError:
            assert i['image'] is None

        try:
            assert isinstance(i['country_code'], str)
            assert i['country_code'] != ""
            assert len(i['country_code']) == 2
        except AssertionError:
            assert i['country_code'] is None

        assert i['type'] == 'identity'






