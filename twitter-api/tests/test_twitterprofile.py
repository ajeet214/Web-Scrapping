import pytest
from modules.twitterprofile import ProfileClass


def search(query):
    obj = ProfileClass()
    return obj.profilefetcher(query)


@pytest.mark.parametrize("user_id", ['realdonaldtrump', 'katyperry'])
def test_twitter_profile(user_id):
    res = search(user_id)

    assert isinstance(res['statuses_count'], int)

    assert isinstance(res['friends_count'], int)

    assert isinstance(res['profile_created_at'], int)

    assert isinstance(res['followers_count'], int)

    assert type(res['verified']) == bool

    assert isinstance(res['favourites_count'], int)

    assert isinstance(res['screen_name'], str)
    assert res['screen_name'] != ""
    assert ' ' not in res['screen_name']

    try:
        assert isinstance(res['name'], str)
        assert res['name'] != ""
    except AssertionError:
        assert res['name'] is None

    try:
        assert isinstance(res['location'], str)
        assert res['location'] != ""
    except AssertionError:
        assert res['location'] is None

    try:
        assert isinstance(res['description'], str)
        assert res['description'] != ""
    except AssertionError:
        assert res['description'] is None

    try:
        assert isinstance(res['profile_image_url'], str)
        assert res['profile_image_url'] != ""
        assert res['profile_image_url'].startswith('http')
    except AssertionError:
        assert res['profile_image_url'] is None

    try:
        assert isinstance(res['profile_banner_url'], str)
        assert res['profile_banner_url'] != ""
        assert res['profile_banner_url'].startswith('http')
    except AssertionError:
        assert res['profile_banner_url'] is None

    try:
        assert isinstance(res['profile_url'], str)
        assert res['profile_url'] != ""
        assert res['profile_url'].startswith('http')
    except AssertionError:
        assert res['profile_url'] is None

    try:
        assert isinstance(res['polarity'], str)
        assert res['polarity'] != ""
        assert res['polarity'] == 'neutral' or res['polarity'] == 'positive' or res['polarity'] == 'negative'
    except AssertionError:
        assert res['polarity'] is None

    assert res['type'] == 'identity'
