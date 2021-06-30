import pytest
from modules.scrap_lookup import ScrapLookup
from modules.lookups import Lookups


@pytest.mark.parametrize("command, domain", [('whois', 'mfa.gov.cn'), ('mx', 'twitter.com')])
def test_lookup(command, domain):
    obj = ScrapLookup()
    res = obj.check_pickle(command, domain)
    checker(res)


# commands MX, A, DNS, SPF, TXT, SOA, PTR
@pytest.mark.parametrize("command, domain", [('mx', 'mfa.gov.cn'), ('spf', 'facebook.com')])
def test_selenium_lookup(command, domain):
    obj = Lookups()
    res = obj.lookups(command, domain)
    checker(res)


def checker(i):

    assert type(i['HasSubscriptions']) == bool
    assert type(i['IsBruteForce']) == bool
    assert type(i['IsEndpoint']) == bool
    assert type(i['IsTransitioned']) == bool
    assert isinstance(i['Information'], list)
    assert isinstance(i['RelatedLookups'], list)

    for j in i['RelatedLookups']:

        try:
            assert isinstance(j['Command'], str)
            assert j['Command'] != ''
        except AssertionError:
            assert j['Command'] is None

        try:
            assert isinstance(j['CommandArgument'], str)
            assert j['CommandArgument'] != ''
        except AssertionError:
            assert j['CommandArgument'] is None

        try:
            assert isinstance(j['Name'], str)
            assert j['Name'] != ''
        except AssertionError:
            assert j['Name'] is None

        try:
            # check for url
            assert isinstance(j['URL'], str)
            assert j['URL'].startswith('http')
        except AssertionError:
            assert j['URL'] is None

    assert isinstance(i['MxRep'], int)

    try:
        # check for non empty string
        assert isinstance(i['DnsServiceProvider'], str)
        assert i['DnsServiceProvider'] != ''
    except AssertionError:
        assert i['DnsServiceProvider'] is None

    try:
        # check for non empty string
        assert isinstance(i['EmailServiceProvider'], str)
        assert i['EmailServiceProvider'] != ''
    except AssertionError:
        assert i['EmailServiceProvider'] is None

    try:
        # check for non empty string
        assert isinstance(i['ReportingNameServer'], str)
        assert i['ReportingNameServer'] != ''
    except AssertionError:
        assert i['ReportingNameServer'] is None

    try:
        # check for non empty string
        assert isinstance(i['CommandArgument'], str)
        assert i['CommandArgument'] != ''
    except AssertionError:
        assert i['CommandArgument'] is None

    try:
        # check for non empty string
        assert isinstance(i['Command'], str)
        assert i['Command'] != ''

    except AssertionError:
        assert i['Command'] is None

    try:
        # check for non empty string
        assert isinstance(i['TimeRecorded'], str)
        assert i['TimeRecorded'] != ''

    except AssertionError:
        assert i['TimeRecorded'] is None

    try:
        assert isinstance(i['Errors'], list)
        assert len(i['Errors']) is 0
    except AssertionError:
        assert i['Errors'] is None


