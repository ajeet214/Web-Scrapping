import pytest
from modules.twittertweets import TwitterClass


@pytest.fixture
def search():
    obj = TwitterClass()
    return obj


@pytest.mark.parametrize("query, limit", [('HappyThanksgiving2018', 44), ('RedmiNote6Pro', 36)])
def test_hashtag(search, query, limit):
    response = search.hashtags(query, limit)
    checker(response)


@pytest.mark.parametrize("query, limit", [('stevewoz', 30), ('politico', 48)])
def test_profiletweets(search, query, limit):
    response = search.profiletweets(query, limit)
    checker(response)


@pytest.mark.parametrize("query, limit", [('tim_cook', 24), ('AppleMusic', 20)])
def test_handlertweets(search, query, limit):
    response = search.handlertweets(query, limit)
    checker(response)


def checker(res):
    for i in res:
        assert type(i['retweet']) == bool
        assert type(i['reply']) == bool
        assert isinstance(i['datetime'], int)
        assert isinstance(i['likes'], int)
        assert isinstance(i['shares'], int)
        assert isinstance(i['polarity'], str)
        assert i['polarity'] == 'neutral' or 'positive' or 'negative'

        try:
            assert isinstance(i['linked_urls'], list)
            assert isinstance(i['linked_urls'][0], str)
            assert i['linked_urls'][0].startswith('http')
        except AssertionError:
            assert i['linked_urls'] is None

        try:
            assert isinstance(i['mentions'], list)
            for j in i['mentions']:
                # each item of list must be a string
                assert isinstance(j, str)
        except AssertionError:
            assert i['mentions'] is None

        try:
            assert isinstance(i['tags'], list)
            for j in i['tags']:
                # each item of list must be a string
                assert isinstance(j, str)
        except AssertionError:
            assert i['tags'] is None

        try:
            # check for url
            assert isinstance(i['url'], str)
            assert i['url'].startswith('http')
        except AssertionError:
            assert i['url'] is None

        try:
            # check for url
            assert isinstance(i['author_url'], str)
            assert i['author_url'].startswith('http')
        except AssertionError:
            assert i['author_url'] is None

        try:
            # check for url
            assert isinstance(i['author_image'], str)
            assert i['author_image'].startswith('http')
        except AssertionError:
            assert i['author_image'] is None

        try:
            # check for non empty string
            assert isinstance(i['author_location'], str)
            assert i['author_location'] != ''
        except AssertionError:
            assert i['author_location'] is None

        try:
            # check for non empty string
            assert isinstance(i['content'], str)
            assert i['content'] != ''
        except AssertionError:
            assert i['content'] is None

        try:
            # check for non empty string
            assert isinstance(i['source'], str)
            assert i['source'] != ''
        except AssertionError:
            assert i['source'] is None

        try:
            # check for non empty string
            assert isinstance(i['author_name'], str)
            assert i['author_name'] != ''
        except AssertionError:
            assert i['author_name'] is None

        try:
            # check for non empty string
            assert isinstance(i['author_userid'], str)
            assert i['author_userid'] != ''
            assert ' ' not in i['author_userid']
        except AssertionError:
            assert i['author_userid'] is None

        try:
            # check for non empty string
            assert isinstance(i['country'], str)
            assert i['country'] != ''
        except AssertionError:
            assert i['country'] is None

        try:
            # check for non empty string
            assert isinstance(i['country_code'], str)
            assert i['country_code'] != ''
            assert len(i['country_code']) == 2
        except AssertionError:
            assert i['country_code'] is None

        try:
            # check for non empty string
            assert isinstance(i['coordinates'], list)
        except AssertionError:
            assert i['coordinates'] is None

        assert i['type'] == 'image' or i['type'] == 'video' or i['type'] == 'status'
