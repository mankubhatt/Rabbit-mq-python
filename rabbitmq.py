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
            time.sleep(45)
            app.logger.info(f"Successfully called ASP.NET API with data: {event_data}")
            ch.basic_ack(delivery_tag=method.delivery_tag)  # send ACK

        except requests.exceptions.HTTPError as err:
            app.logger.error(f"Failed to call ASP.NET API. Error: {err}")
            ch.basic_nack(delivery_tag=method.delivery_tag)  # send NACK, message will be requeued

    elif event_type == 'Mayank Event':
        try:
            time.sleep(15)
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
    with app.app_context():  # pushing the application context
        while True:
            try:
                connection = pika.BlockingConnection(parameters)
                channel = connection.channel()
                # channel.basic_qos(prefetch_count=1)  # Add this line
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

            except Exception as e:  # change here to catch all exceptions
                app.logger.error(f"An error occurred: {e}. Trying to reconnect in {reconnect_delay} seconds.")
                time.sleep(reconnect_delay)
                # increase the delay for next reconnection attempt
                reconnect_delay *= 2


def publish_message(event_type, event_data, priority=0, app=None):  # added priority and app as arguments
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Declare the queue with x-max-priority argument
    arguments = {'x-max-priority': 10}
    channel.queue_declare(queue='event_queue', durable=True, arguments=arguments)

    message_body = json.dumps({
        'type': event_type,
        'data': event_data
    })

    print(priority, "hello")
    properties = pika.BasicProperties(
        delivery_mode=2,  # make message persistent
        priority=priority  # set message priority
    )

    channel.basic_publish(
        exchange='',
        routing_key='event_queue',
        body=message_body,
        properties=properties
    )

    if app:  # only log if app is provided
        app.logger.info(f"Sent {message_body}")
    connection.close()
