# Using flask server


## Run the flask app

`gunicorn -w 3 -b 127.0.0.1:8000 app:app`

## Run the test (consumer generates the contract)

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
      "providerState": "team_karoo exists",
      "description": "a request for user team_karoo",
      "request": {
        "method": "get",
        "path": "/users/team_karoo"
      },
      "response": {
        "status": 200,
        "body": {
          "name": "team_karoo"
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

Use the pactman-verifier or pact-verifier command-line program which replays the pact assertions against a running instance of your service.

`pactman-verifier -l Consumer-Provider-pact.json Provider http://localhost:8000 http://localhost:8000/_pact/provider_states`

OR

`pact-verifier --provider-base-url=http://localhost:8000 --pact-url=Consumer-Provider-pact.json --provider-states-setup-url=http://localhost:8000/_pact/provider_states`

Result should like:


```
Consumer: Consumer
Request: "a request for user team_karoo" ... PASSED
 Using provider state 'team_karoo exists'

```
OR

```
INFO: Reading pact at Consumer-Provider-pact.json

Verifying a pact between Consumer and Provider
  Given team_karoo exists
    a request for user team_karoo
      with GET /users/team_karoo
        returns a response which
          has status code 200
          has a matching body

1 interaction, 0 failures

```
