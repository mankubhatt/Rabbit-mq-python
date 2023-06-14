import logging
from logging.handlers import TimedRotatingFileHandler


def create_logger(app):
    handler = TimedRotatingFileHandler('app.log', when='midnight', interval=1, backupCount=30)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S'))

    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    return app.logger
