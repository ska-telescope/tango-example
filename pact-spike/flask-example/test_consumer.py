import pytest
from pactman import Consumer, Provider, Term
from consumer import get_user


@pytest.fixture
def pact(monkeypatch):
    pact = Consumer('Consumer').has_pact_with(Provider('Provider'))
    pact.start_service()
    monkeypatch.setattr('consumer.get_url', lambda: pact.uri)
    yield pact
    pact.stop_service()


def test_get_user(pact):
    expected = {
        'name': 'team_karoo'}

    (pact
     .given('team_karoo exists')
     .upon_receiving('a request for user team_karoo')
     .with_request('get', '/users/team_karoo')
     .will_respond_with(200, body=expected))

    with pact:
        result = get_user('team_karoo')
    assert result == expected
