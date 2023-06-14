from threading import Thread
from rabbitmq import consume_events
from app import create_app
import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    consumer_thread = Thread(target=consume_events, args=(app,))  # passing app as an argument
    consumer_thread.start()
    app.run(port=5000, debug=True)
