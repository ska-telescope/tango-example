import pytest
from functools import partial
from pactman import Consumer, Provider, Term
from consumer import get_attribute


@pytest.fixture
def pact():
    pact = Consumer('Consumer').has_pact_with(Provider('CalendarClock'))
    pact.start_service()
    yield pact
    pact.stop_service()


def test_get_attribute(pact):
    endpoint = ("/tango/rest/rc4/hosts/sam-XPS-15-9570/10000/devices/test/calendarclockdevice"
                "/1/attributes/calendar_date/value")

    regex = r'^1[0-9]{12}$'
    sample_timestamp = '1596416329618'
    expected = {
        'name': 'calendar_date',
        'value': '03/02/0001',
        'quality': 'ATTR_VALID',
        'timestamp': Term(regex, sample_timestamp)
    }

    (pact
     .given('calendarclockdevice is running')
     .upon_receiving('a request for calendar_date attribute')
     .with_request('get', endpoint)
     .will_respond_with(200, body=expected))

    with pact:
        result = get_attribute(pact.uri, endpoint)
        assert result['value'] == '03/02/0001'
