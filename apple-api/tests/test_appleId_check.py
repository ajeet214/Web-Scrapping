import pytest
from modules.appleId_check import AppleId


def search(query):
    obj = AppleId()
    result = obj.id_check(query)
    return result


@pytest.mark.parametrize("id", ['austinpaul134@outlook.com', 'jaqsoms43@gmail.com'])
def test_id_checker(id):
    result1 = search(id)
    assert type(result1['profileExists']) == bool


