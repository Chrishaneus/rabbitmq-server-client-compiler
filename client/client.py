#!/usr/bin/env python
import pika
import uuid
import os
import json

# read rabbitmq connection url from environment variable
amqp_url = os.environ['AMQP_URL']
url_params = pika.URLParameters(amqp_url)

class CompilationRpcClient(object):

    def __init__(self):
        self.connection = pika.BlockingConnection(url_params)

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body)

    def compile(self, code, lang, tests, filename = "temp"):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps({
                'code' : code,
                'lang' : lang,
                'tests' : tests,
                'filename' : filename
            }))
        self.connection.process_data_events(time_limit=None)
        return self.response


compilation_rpc = CompilationRpcClient()

print(" [x] Requesting compilation results")
response = compilation_rpc.compile(
    code="""
var prompt = require('prompt-sync')();
var n = prompt('My input! ');
""",
    lang="javascript",
    tests=["aefiaji", "efiajij"],
    filename="someuid"
)

from pprint import pprint
pprint(" [ ] SUCCESSFULLY RETURNED!")
pprint(response)