import pytest
from flask import Flask
from app.index_views import index_views  # replace with your actual module name


def create_test_app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(index_views)

    return app


@pytest.fixture
def test_client():
    flask_app = create_test_app()

    testing_client = flask_app.test_client()
    context = flask_app.app_context()
    context.push()

    yield testing_client  # this is where the testing happens!

    context.pop()


def test_health_check(test_client):
    response = test_client.get('/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'success'}
