import pytest
from modules.Id_checker import EmailChecker


def search(query):
    obj = EmailChecker()
    return obj.checker(query)


@pytest.mark.parametrize("query", ['918619489612', 'justinmat1994@outlook.com'])
def test_id_checker(query):
    res = search(query)

    try:
        assert type(res['profileExists']) == bool
    except AssertionError:
        assert res is None
