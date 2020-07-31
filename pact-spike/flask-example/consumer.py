import requests
import sys

def get_url():
    return "http://localhost:8000"

def get_user(user_name):
    """Fetch a user object by user_name from the server."""
    user = requests.get(f'{get_url()}/users/{user_name}')
    return user.json()
