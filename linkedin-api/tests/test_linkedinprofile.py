import pytest
from modules.linkedinprofile import ProfileFetcher


@pytest.mark.parametrize("userid", ['eric-hargrave-2aa704b', 'alain-djie-09b323'])
def test_profile_fetcher(userid):
    obj = ProfileFetcher()
    res = obj.Porfile(userid)

    assert type(res['status']) == bool

    try:
        assert isinstance(res['profile_url'], str)
        assert res['profile_url'] is not ""
        assert res['profile_url'].startswith('http')
    except:
        assert res['profile_url'] is None

    try:
        assert isinstance(res['summary']['firstName'], str)
        assert res['summary']['firstName'] is not ""
    except:
        assert res['summary']['firstName'] is None

    try:
        assert isinstance(res['summary']['lastName'], str)
        assert res['summary']['lastName'] is not ""
    except:
        assert res['summary']['lastName'] is None

    try:
        assert isinstance(res['summary']['locationName'], str)
        assert res['summary']['locationName'] is not ""
    except:
        assert res['summary']['locationName'] is None

    try:
        assert isinstance(res['summary']['headline'], str)
        assert res['summary']['headline'] is not ""
    except:
        assert res['summary']['headline'] is None

    try:
        assert isinstance(res['summary']['image'], str)
        assert res['summary']['image'] is not ""
        assert res['summary']['image'].startswith('http')
    except:
        assert res['summary']['image'] is None

    try:
        assert isinstance(res['summary']['industryName'], str)
        assert res['summary']['industryName'] is not ""
    except:
        assert res['summary']['industryName'] is None

    try:
        assert isinstance(res['summary']['birthDate'], str)
        assert res['summary']['birthDate'] is not ""
    except:
        assert res['summary']['birthDate'] is None
