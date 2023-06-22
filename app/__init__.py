from flask import Flask
from flask_jwt_extended import JWTManager
from config import config
from .limiter import limiter
from .logger_config import create_logger  # make sure to import your function
from datetime import timedelta
from .auth_views import auth_views
from .event_views import event_views
from .index_views import index_views
from .services.rabbitmq_producer import init_app as rabbitmq_producer_init_app
from .services.rabbitmq_consumer import init_app as rabbitmq_consumer_init_app


jwt = JWTManager()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Add this line
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this!
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=60)  # Add this line

    limiter.init_app(app)
    jwt.init_app(app)  # Add this line

    # Initialize logger
    app.logger = create_logger(app)

    app.register_blueprint(auth_views)
    app.register_blueprint(event_views)
    app.register_blueprint(index_views)

    rabbitmq_producer_init_app(app)
    rabbitmq_consumer_init_app(app)

    return app
