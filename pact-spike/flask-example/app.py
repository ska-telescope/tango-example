#!~/usr/bin/python3
import datetime
from flask import abort, Flask, jsonify, request

fakedb = {}

app = Flask(__name__)

def setup_user():
    fakedb['team_karoo'] = {'name': "team_karoo"}

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/users/<user_name>')
def get_user(user_name):
    user_data = fakedb.get(user_name)
    if not user_data:
        abort(404)
    response = jsonify(**user_data)
    return response

@app.route('/_pact/provider_states', methods=['POST'])
def provider_states():
    mapping = {'team_karoo exists': setup_user}
    mapping[request.json['state']]()
    return jsonify({'result': request.json['state']})

if __name__ == '__main__':
    app.run(debug=True)
