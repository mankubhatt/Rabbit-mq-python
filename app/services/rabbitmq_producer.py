import json
import pika

parameters = None
reconnect_delay = 5  # initial time delay in seconds to attempt reconnection
ASP_API_URL = None


def init_app(flask_app):
    global parameters, ASP_API_URL
    parameters = pika.ConnectionParameters(host=flask_app.config['RABBITMQ_HOST'])
    ASP_API_URL = flask_app.config['ASP_API_URL']


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
