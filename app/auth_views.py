from flask import Blueprint, request, jsonify, current_app as app
from flask_jwt_extended import create_access_token
from flasgger import swag_from


auth_views = Blueprint('auth', __name__)


@auth_views.route('/generate-token', methods=['POST'])
@swag_from('yaml/generate-token.yml')
def generate_token():
    api_key = request.json.get('api_key', None)
    if not api_key or api_key != app.config['API_KEY']:
        return jsonify({'message': 'Invalid API key'}), 401

    # Identity can be anything such as a server name, etc.
    access_token = create_access_token(identity=api_key)
    return jsonify(access_token=access_token)
