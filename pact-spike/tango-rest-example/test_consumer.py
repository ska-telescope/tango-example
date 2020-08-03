import pytest
from functools import partial
from pactman import Consumer, Provider, Term
from consumer import get_attribute


@pytest.fixture
def pact():
    pact = Consumer('Consumer').has_pact_with(Provider('Provider'))
    pact.start_service()
    yield pact
    pact.stop_service()


def test_get_user(pact):
    endpoint = ("/tango/rest/rc4/hosts/sam-XPS-15-9570/10000/devices/test/calendarclockdevice"
                "/1/attributes/calendar_date/value")

    regex = r'^1[0-9]{12}$'
    sample_data = '1596416329618'
    expected = {
        'name': 'calendar_date',
        'value': '03/02/0001',
        'quality': 'ATTR_VALID',
        'timestamp': Term(regex, sample_data)
    }

    (pact
     .given('calendarclockdevice is running')
     .upon_receiving('a request for calendar_date attribute')
     .with_request('get', endpoint)
     .will_respond_with(200, body=expected))

    with pact:
        result = get_attribute(pact.uri, endpoint)
    # generate the timestamp from the Term object
    expected['timestamp'] = expected['timestamp'].generate
    assert result == expected
