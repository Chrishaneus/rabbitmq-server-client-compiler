#!/usr/bin/env python
import pika, os, json
from compiler.compile import compile

amqp_url = os.environ['AMQP_URL']
url_params = pika.URLParameters(amqp_url)

connection = pika.BlockingConnection(url_params)

channel = connection.channel()

channel.queue_declare(queue='compiler_queue')

def on_request(ch, method, props, body):
    details = json.loads(body)
    response = compile(details['code'], details['lang'], details['tests'], details['filename'])

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=json.dumps(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='compiler_queue', on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
channel.start_consuming()