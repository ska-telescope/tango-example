#!~/usr/bin/python3
"""A flask application that accesses the tango rest server to query running devices"""

import requests
from flask import abort, Flask, jsonify, request
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

GATEWAY = "http://localhost:8080"
ENDPOINT = ("/tango/rest/rc4/hosts/sam-XPS-15-9570/10000/devices/test")

def is_device_running(dev_name):
    user = 'tango-cs'
    passwd = 'tango'
    url = f'{GATEWAY}{ENDPOINT}'
    response = requests.get(url, auth=HTTPBasicAuth(user, passwd))
    devices = response.json()
    return dev_name in devices


@app.route('/_pact/provider_states', methods=['POST'])
def provider_states():
    mapping = {'calendarclockdevice is running': "calendarclockdevice"}
    dev_name = mapping[request.json['state']]
    if not is_device_running(dev_name):
        abort(404)
    return jsonify({'result': request.json['state']})

if __name__ == '__main__':
    app.run(debug=True)
