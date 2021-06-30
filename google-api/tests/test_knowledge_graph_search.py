import pytest
from modules.knowledge_graph_search import KnowledgeGraphSearch


def Object(query, limit):
    obj = KnowledgeGraphSearch()
    result = obj.knowledge_search(query, limit)
    return result


@pytest.mark.parametrize("name, limit", [('bill gates', 50), ('Nguyễn Xuân', 30)])
def test_knowledge_search(name, limit):
    result1 = Object(name, limit)
    for i in result1['data']['results']:

        try:
            assert type(i['id']) == str
            # assert i['url'].startswith('http')
            assert i['id'] != ""
        except:
            assert i['id'] is None

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
            assert i['description'] != ""
            assert type(i['description']) == str
        except:
            assert i['description'] is None


        try:
            assert i['linked_url'] != ""
            assert type(i['linked_url']) == str
        except:
            assert i['linked_url'] is None

        try:
            assert i['profile_url'] != ""
            assert type(i['profile_url']) == str
        except:
            assert i['profile_url'] is None

        try:
            assert i['profile_name'] != ""
            assert type(i['profile_name']) == str
        except:
            assert i['profile_name'] is None

        try:
            assert i['profile_image'] != ""
            assert type(i['profile_image']) == str
        except:
            assert i['profile_image'] is None

        try:
            assert i['image_url'] != ""
            assert type(i['image_url']) == str
        except:
            assert i['image_url'] is None

        assert type(i['category']) == list



