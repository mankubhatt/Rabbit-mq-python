from flask import Blueprint, request, jsonify, current_app as app
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields, ValidationError
from . import limiter
from .services.rabbitmq_producer import publish_message

event_views = Blueprint('event', __name__)


class EventSchema(Schema):
    event_type = fields.Str(required=True)
    event_data = fields.Str(required=True)
    priority = fields.Int(required=False)


event_schema = EventSchema()


@event_views.route('/publish', methods=['POST'])
@limiter.limit("100/minute")
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
