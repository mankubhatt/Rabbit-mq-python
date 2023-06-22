from threading import Thread
from app.services.rabbitmq_consumer import consume_events
from app import create_app
import os


def consume_events_with_error_handling(app):
    while True:
        try:
            consume_events(app)
        except Exception as e:
            app.logger.error(f"Error in consumer thread: {e}")


app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    consumer_thread = Thread(target=consume_events_with_error_handling, args=(app,))  # Change here
    consumer_thread.start()
    app.run(port=5000, debug=True)
