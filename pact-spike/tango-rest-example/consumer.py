import sys
import requests
from requests.auth import HTTPBasicAuth


# GATEWAY = "http://localhost:8080"

# ENDPOINT = ("tango/rest/rc4/hosts/sam-XPS-15-9570/10000/devices/test/"
#             "calendarclockdevice/1/attributes")

def get_attribute(GATEWAY, ENDPOINT):
    """Fetch an attribute from device running on the rest server."""
    user = 'tango-cs'
    passwd = 'tango'
    url = f'{GATEWAY}{ENDPOINT}'
    attr_value = requests.get(url, auth=HTTPBasicAuth(user, passwd))
    return attr_value.json()

if __name__ == '__main__':
    GATEWAY, ENDPOINT = sys.argv[1:]
    print(get_attribute(GATEWAY, ENDPOINT))
