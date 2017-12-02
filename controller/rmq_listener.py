#!/usr/bin/env python

import pika
import json
import urllib2


AQMP_URL = 'amqp://app:app@always.cs.uchicago.edu:5672/always.cs.uchicago.edu'
API_SERVER = 'always.cs.uchicago.edu'
API_PORT = 8000


def callback(ch, method, properties, body):
    #print(" [x] Received %r" % body)
    print("New Item on Queue")

    try:
        req = urllib2.Request('http://' + API_SERVER + ':' + str(API_PORT) + '/api/crawleditems/')
        req.add_header('Content-Type', 'application/json')
        urllib2.urlopen(req, body)
    except urllib2.HTTPError as e:
        error_message = e.read()
        print error_message


def main():
    connection = pika.BlockingConnection(pika.URLParameters(AQMP_URL))
    channel = connection.channel()

    channel.queue_declare(queue='discover')
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.basic_consume(callback, queue='discover', no_ack=True)
    channel.start_consuming()


if __name__ == '__main__':
    main()
