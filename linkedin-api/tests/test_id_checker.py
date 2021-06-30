import pytest
from modules.Id_checker import LinkedinId


@pytest.mark.parametrize("email", ["pparkar549@gmail.com", "quality.slip2016@ydex.com"])
def test_id_checker(email):
    obj = LinkedinId()
    res = obj.id_check(email)

    assert isinstance(res['profile'], str)
    assert type(res['profileExists']) == bool
