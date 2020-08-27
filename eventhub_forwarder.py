#!/usr/bin/env python

import time
import os
import sys
import json

from datetime import datetime, timedelta
from azure.eventhub import EventHubProducerClient
from azure.eventhub.exceptions import EventHubError
from azure.eventhub import EventData
from nginx.controller import Controller

CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']
CONTROLLER_USER = os.environ['CONTROLLER_USER']
CONTROLLER_PASS = os.environ['CONTROLLER_PASS']
BATCH_SIZE = 3
SLEEP_PERIOD = 10

def send_event_data_batch(producer, events, start):
    ecount = 0
    submissions = sorted(events['items'], key=lambda x:x['timestamp'])
    event_data_batch = producer.create_batch()
    for event in submissions:
        ecount += 1
        next_uuid = event['id']
        next_timestamp = event['timestamp']

        print("EventHub Forwarder Batching {}: {}".format(event['id'], event['timestamp']))
        event_data = EventData(json.dumps(event));
        event_data_batch.add(event_data)

        if ((ecount % BATCH_SIZE == 0) or ( ecount == len(events['items']))): 
            print("EventHub Forwarder Sending {} events".format( BATCH_SIZE if ( ecount % BATCH_SIZE == 0 ) else ( ecount % BATCH_SIZE)  ))
            try:
                producer.send_batch(event_data_batch)
                if ( next_uuid is not "deadbeef-dead-beef-dead-999999999999"):
                    start = next_timestamp
                event_data_batch = producer.create_batch()
            except ValueError:
                print("ERROR Batch too large")
                break;
            except EventHubError as eh_err:
                print("ERROR: ", eh_err)
                break;

    dt = datetime.strptime(start, '%Y-%m-%dT%H:%M:%SZ') + timedelta(seconds=1)
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ');

print("EventHub Forwarder Starting Up")
producer = EventHubProducerClient.from_connection_string(
    conn_str=CONNECTION_STR,
    eventhub_name=EVENTHUB_NAME
)

print("EventHub Forwarder Logging in to Controller")
ngxctl = Controller('localhost', CONTROLLER_USER, CONTROLLER_PASS)
if ( ngxctl.login() is False ):
    print("ERROR - NGINX Controller Login failed")
    sys.exit(1)

start = None
events = None
RUN = True
print("EventHub Forwarder Entering main loop")
while RUN is True:
    last_events = events
    if start is None:
        events = ngxctl.get_events(period="1m")
    else:
        events = ngxctl.get_events_since(start)

    if ( len(events['items']) == 0 ):
        time.sleep(SLEEP_PERIOD)
        continue

    print("EventHub Forwarder Collected: {} events".format(len(events['items'])))
    start = send_event_data_batch(producer, events, start)
    print("EventHub Forwarder Next: {}".format(start))
    time.sleep(1)

print("EventHub Forwarder Exiting")

