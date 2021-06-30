import pytest
from modules.googleVideo import GoogleVideo


def Object(query):
    obj = GoogleVideo()
    result = obj.get(query)
    return result


@pytest.mark.parametrize("name", ['steven', 'Nguyễn'])
def test_video_search(name):
    result1 = Object(name)
    for i in result1:
        try:
            assert type(i['url']) == str
            # assert i['url'].startswith('http')
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
            assert i['thumbnail'] != ""
            assert type(i['thumbnail']) == str
        except:
            assert i['thumbnail'] is None

        assert i['type'] is 'video'






