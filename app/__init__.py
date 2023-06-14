from flask import Flask
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter, util
from config import config
from .logger_config import create_logger  # make sure to import your function
from datetime import timedelta


limiter = Limiter(key_func=util.get_remote_address)
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

    from .views import views as views_blueprint
    app.register_blueprint(views_blueprint)

    from rabbitmq import init_app as rabbitmq_init_app
    rabbitmq_init_app(app)

    return app
