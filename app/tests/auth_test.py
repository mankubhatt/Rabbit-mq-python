import pytest
from flask import Flask
from app.auth_views import auth_views


def create_test_app():
    app = Flask(__name__)
    app.config['API_KEY'] = 'test_api_key'
    app.config['JWT_SECRET_KEY'] = 'test_jwt_secret_key'
    app.config['TESTING'] = True
    app.register_blueprint(auth_views)

    return app


@pytest.fixture
def test_client():
    flask_app = create_test_app()

    testing_client = flask_app.test_client()
    context = flask_app.app_context()
    context.push()

    yield testing_client  # this is where the testing happens!

    context.pop()


def test_generate_token_success(test_client):
    response = test_client.post('/generate-token', json={'api_key': 'test_api_key'})
    assert response.status_code == 200
    assert 'access_token' in response.get_json()


def test_generate_token_fail(test_client):
    response = test_client.post('/generate-token', json={'api_key': 'wrong_api_key'})
    assert response.status_code == 401
    assert response.get_json() == {'message': 'Invalid API key'}
