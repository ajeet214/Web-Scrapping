import pytest
from modules.emailChecker import EmailChecker


def Object(id):
    obj = EmailChecker()
    result = obj.checker(id)
    return result


@pytest.mark.parametrize("gmail_id" , ["justinmat1994@gmail.com", "veronikascott27@gmail.com"])
def test_email_checker(gmail_id):
    res = Object(gmail_id)

    assert type(res['email']) == bool
    # assert type(res['googlePlusId']) == str

    try:
        assert res['email_id'] != ""
        assert type(res['email_id']) == str
    except:
        assert res['email_id'] is None

    try:
        assert res['name'] != ""
        assert type(res['name']) == str
    except:
        assert res['name'] is None

    try:
        assert res['image'] != ""
        assert type(res['image']) == str
    except:
        assert res['image'] is None



