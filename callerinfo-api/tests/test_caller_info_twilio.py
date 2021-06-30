import pytest
from modules.caller_info_twilio import NumberInfo


@pytest.mark.parametrize('number', ['+51962070639', '+46735842206'])
def test_caller_info(number):
    obj = NumberInfo()
    res = obj.caller_data(number)

    try:
        assert len(res['country_code']) is 2
        assert isinstance(res['country_code'], str)
        assert res['country_code'] is not ''
    except AssertionError:
        assert res['country_code'] is None

    try:
        assert isinstance(res['country'], str)
        assert res['country'] is not ''
    except AssertionError:
        assert res['country'] is None

    try:
        assert isinstance(res['number_type'], str)
        assert res['number_type'] is not ''
    except AssertionError:
        assert res['number_type'] is None

    try:
        assert isinstance(res['carrier_name'], str)
        assert res['carrier_name'] is not ''
    except AssertionError:
        assert res['carrier_name'] is None

    try:
        assert isinstance(res['number'], str)
        assert res['number'] is not ''
    except AssertionError:
        assert res['number'] is None

    try:
        assert isinstance(res['mobile_network_code'], str)
        assert res['mobile_network_code'] is not ''
    except AssertionError:
        assert res['mobile_network_code'] is None

    try:
        assert isinstance(res['national_format'], str)
        assert res['national_format'] is not ''
    except AssertionError:
        assert res['national_format'] is None

    try:
        assert isinstance(res['mobile_country_code'], str)
        assert res['mobile_country_code'] is not ''
        assert len(res['mobile_country_code']) < 4

    except AssertionError:
        assert res['mobile_country_code'] is None

    try:
        assert isinstance(res['geo_location']['longitude'], str)
        assert res['geo_location']['longitude'] is not ''
        assert isinstance(res['geo_location']['latitude'], str)
        assert res['geo_location']['latitude'] is not ''
    except AssertionError:
        assert res['geo_location']['longitude'] is None
        assert res['geo_location']['latitude'] is None
