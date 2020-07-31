# Using flask server


## Run the tango rest server and the calendar clock device

`make up`

## Test the tango rest server accepts the request

`python consumer.py http://localhost:8080 /tango/rest/rc4/hosts/sam-XPS-15-9570/10000/devices/test/calendarclockdevice/1/attributes/calendar_date/value`

This will return `{'name': 'calendar_date', 'value': '03/02/0001', 'quality': 'ATTR_VALID', 'timestamp': 1596113122747}`

## Run the test: consumer generates the contract

`pytest`


A json file with name `Consumer-Provider-pact.json` should be generated: this is your PACT file. Contents will look like:
```
{
  "consumer": {
    "name": "Consumer"
  },
  "provider": {
    "name": "Provider"
  },
  "interactions": [
    {
      "providerState": "calendarclock device is running",
      "description": "a request for calendar_date attribute",
      "request": {
        "method": "get",
        "path": "/tango/rest/rc4/hosts/sam-XPS-15-9570/10000/devices/test/calendarclockdevice/1/attributes/calendar_date/value"
      },
      "response": {
        "status": 200,
        "body": {
          "name": "calendar_date",
          "value": "03/02/0001",
          "quality": "ATTR_VALID",
          "timestamp": 1596109330329
        }
      }
    }
  ],
  "metadata": {
    "pactSpecification": {
      "version": "2.0.0"
    }
  }
}

```

## Provider verifies the contract

`pact-verifier --provider-base-url=http://localhost:8000 --pact-url=Consumer-Provider-pact.json`

Result should like:

```
INFO: Reading pact at Consumer-Provider-pact.json

Verifying a pact between Consumer and Provider
  Given team_karoo exists
    a request for user team_karoo
      with GET /users/team_karoo
        returns a response which
WARN: Skipping set up for provider state 'team_karoo exists' for consumer 'Consumer' as there is no --provider-states-setup-url specified.
          has status code 200
          has a matching body

1 interaction, 0 failures

```