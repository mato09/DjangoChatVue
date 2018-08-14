import sys

import pika
import uwsgi


def application(env, start_response):
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost')
    )
    channel = connection.channel()

    exchange = env['PATH_INFO'].replace('/', '')

    channel.exchange_declare(
        exchange=exchange, exchange_type='fanout'
    )

    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue  # generate RabbitMQ random

    channel.queue_bind(exchange=exchange, queue=queue_name)

    uwsgi.websocket_handshake(
        env['HTTP_SEC_WEBSOCKET_KEY'],
        env.get('HTTP_ORIGIN', '')
    )

    def keepalive():
        # hidup 30 detik
        print('PING/PONG...')
        try:
            uwsgi.websocket_recv_nb()
            connection.add_timeout(30, keepalive)
        except OSError as error:
            print(error)
            sys.exit(1) # Kill process and force uWSGI to Respawn

    keepalive()

    while True:
        for method_frame, _, body in channel.consume(queue_name):
            try:
                uwsgi.websocket_send(body)
            except OSError as error:
                print(error)
                sys.exit(1) 
            else:
                channel.basic_ack(method_frame.delivery_tag)
