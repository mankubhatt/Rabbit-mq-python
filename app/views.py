from flask import Blueprint, request, jsonify, current_app as app
from flask_jwt_extended import create_access_token, jwt_required
from marshmallow import Schema, fields, ValidationError
from . import limiter
from rabbitmq import publish_message

views = Blueprint('views', __name__)


class EventSchema(Schema):
    event_type = fields.Str(required=True)
    event_data = fields.Str(required=True)
    priority = fields.Int(required=False)


event_schema = EventSchema()


@views.route('/publish', methods=['POST'])
@limiter.limit("10/minute")
@jwt_required()
def publish_event():
    try:
        data = event_schema.loads(request.data)
        priority = data.get('priority', 0)  # default priority to 0 if not specified
        publish_message(data['event_type'], data['event_data'], priority, app)  # pass app and priority
        app.logger.info(f'Published message: {data}')  # Use Flask app logger
        return jsonify(status='success'), 200
    except ValidationError as e:
        app.logger.error('Invalid request body')  # Use Flask app logger
        return jsonify(error='Invalid request body', details=e.messages), 400
    except Exception as e:
        app.logger.error(str(e))  # Use Flask app logger
        return jsonify(error='An unexpected error occurred'), 500


@views.route('/generate-token', methods=['POST'])
def generate_token():
    api_key = request.json.get('api_key', None)
    if not api_key or api_key != app.config['API_KEY']:
        return jsonify({'message': 'Invalid API key'}), 401

    # Identity can be anything such as a server name, etc.
    access_token = create_access_token(identity=api_key)
    return jsonify(access_token=access_token)


@views.route('/health', methods=['GET'])
def health_check():
    app.logger.info(f'Health Check')  # Use Flask app logger
    return jsonify(status='success'), 200
