import pytest
import unittest.mock as mock
from flask import Flask
from app.event_views import event_views  # replace with your actual module name


def create_test_app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(event_views)

    return app


@pytest.fixture
def test_client():
    flask_app = create_test_app()

    testing_client = flask_app.test_client()
    context = flask_app.app_context()
    context.push()

    yield testing_client  # this is where the testing happens!

    context.pop()


@mock.patch('your_module.limiter')
@mock.patch('your_module.jwt_required')
@mock.patch('your_module.publish_message')
def test_publish_event_success(mock_publish_message, mock_jwt_required, mock_limiter, test_client):
    mock_jwt_required.return_value = lambda x: x  # override the jwt_required decorator
    mock_limiter.return_value = lambda x: x  # override the limiter decorator

    event = {
        'event_type': 'test_event',
        'event_data': {'test': 'data'},
    }

    response = test_client.post('/publish', json=event)
    assert response.status_code == 200
    assert response.get_json() == {'status': 'success'}

    # Check if publish_message was called with correct arguments
    mock_publish_message.assert_called_once_with('test_event', {'test': 'data'}, 0, mock.ANY)
