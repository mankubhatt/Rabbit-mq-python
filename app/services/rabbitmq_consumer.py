import json
import requests
import time
import pika

parameters = None
reconnect_delay = 5  # initial time delay in seconds to attempt reconnection
ASP_API_URL = None


def init_app(flask_app):
    global parameters, ASP_API_URL
    parameters = pika.ConnectionParameters(host=flask_app.config['RABBITMQ_HOST'])
    ASP_API_URL = flask_app.config['ASP_API_URL']


def callback(ch, method, properties, body, app):  # added app as an argument
    event = json.loads(body)
    event_type = event.get('type')
    event_data = event.get('data')

    app.logger.info(f"Received event type {event_type} with data {event_data}")

    if event_type == 'Example Event':
        try:
            time.sleep(15)
            app.logger.info(f"Successfully called ASP.NET API with data: {event_data}")
            ch.basic_ack(delivery_tag=method.delivery_tag)  # send ACK

        except requests.exceptions.HTTPError as err:
            app.logger.error(f"Failed to call ASP.NET API. Error: {err}")
            ch.basic_nack(delivery_tag=method.delivery_tag)  # send NACK, message will be requeued

    elif event_type == 'Mayank Event':
        try:
            time.sleep(5)
            app.logger.info(f"Successfully called ASP.NET API with data: {event_type}")
            ch.basic_ack(delivery_tag=method.delivery_tag)  # send ACK

        except requests.exceptions.HTTPError as err:
            app.logger.error(f"Failed to call ASP.NET API. Error: {err}")
            ch.basic_nack(delivery_tag=method.delivery_tag)  # send NACK, message will be requeued

    else:
        app.logger.warning(f"Unknown event type received: {event_type}")
        ch.basic_ack(delivery_tag=method.delivery_tag)  # ACK unknown event types to remove them from queue


def consume_events(app):  # added app as an argument
    global reconnect_delay
    max_retries = 5  # maximum number of retries
    current_retries = 0  # counter for current retries
    with app.app_context():  # pushing the application context
        while current_retries <= max_retries:
            try:
                connection = pika.BlockingConnection(parameters)
                channel = connection.channel()
                # Declare the queue with x-max-priority argument
                arguments = {'x-max-priority': 10}
                channel.queue_declare(queue='event_queue', durable=True, arguments=arguments)
                channel.basic_consume(queue='event_queue',
                                      on_message_callback=lambda ch, method, properties, body: callback(ch, method,
                                                                                                        properties,
                                                                                                        body, app),
                                      auto_ack=False)  # passing app to the callback

                app.logger.info('Waiting for messages. To exit press CTRL+C')
                channel.start_consuming()

                # reset the delay if connection is successful
                reconnect_delay = 5
                current_retries = 0  # reset retries count on successful connection

            except Exception as e:  # change here to catch all exceptions
                app.logger.error(f"An error occurred: {e}. Trying to reconnect in {reconnect_delay} seconds.")
                time.sleep(reconnect_delay)
                # increase the delay for next reconnection attempt
                reconnect_delay *= 2
                current_retries += 1  # increment retries count after a failed attempt

        # if loop has exited due to max_retries being reached
        if current_retries > max_retries:
            app.logger.error(f"Maximum number of retries ({max_retries}) reached. Stopping consumer.")
