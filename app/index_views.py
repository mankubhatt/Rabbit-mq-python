from flask import Blueprint, jsonify, current_app as app

index_views = Blueprint('index', __name__)


@index_views.route('/health', methods=['GET'])
def health_check():
    app.logger.info(f'Health Check')  # Use Flask app logger
    return jsonify(status='success'), 200
