import pytest
from modules.wikipedia import Wikipedia


@pytest.mark.parametrize('query, limit',[('donald trump', 40), ('Nguyễn Xuân Phúc', 32)] )
def test_wikipedia(query, limit):
    obj = Wikipedia()
    res = obj.search(query, limit)

    for i in res['data']:

        try:
            assert isinstance(i['url'], str)
            assert i['url'] is not ''
            assert i['url'].startswith('http')
        except:
            assert i['url'] is None

        try:
            assert isinstance(i['title'], str)
            assert i['title'] is not ''
        except:
            assert i['title'] is None

        try:
            assert isinstance(i['content'], str)
            assert i['content'] is not ''
        except:
            assert i['content'] is None

        assert i['polarity'] is 'neutral' or 'positive' or 'negative'

        assert i['type'] is 'link'
