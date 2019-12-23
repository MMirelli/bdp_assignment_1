import pika
from pika.exceptions import AMQPConnectionError
from pika.exceptions import ConnectionClosedByBroker
from pika.exceptions import StreamLostError

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
from cassandra.cluster import NoHostAvailable
from cassandra import InvalidRequest

from datetime import datetime as dt
import time

import logging

format = "%(asctime)s >> %(message)s"
logging.basicConfig(format=format,
                        datefmt="%H:%M:%S")

logging.getLogger("pika").setLevel(logging.CRITICAL)
logging.getLogger("cassandra").setLevel(logging.CRITICAL)
logger = logging.getLogger("client")

logger.setLevel(logging.INFO)

def dequeue(body):
    values = body.decode("utf8").split(';')
#    print(values) # logger
    return values
    
def format_date(d):
    data_format = "%m/%d/%Y %I:%M:%S %p"
    cas_format = "%Y-%m-%d %H:%M:%S"

    d = dt.strptime(d, data_format)
    return d.strftime(cas_format)
    
def format_batch(body):
    formatted_body = []
    for s in body:
        val = s.split(',')
        val[1] = '\'%s\'' % format_date(val[1])
        val[2] = '\'%s\'' % format_date(val[2])
        val[6] = 'true' if val[6] == 'Y' else 'false'
        s = ','.join(val)
        formatted_body.append(s)
    del_i = formatted_body[-1].find("|")
    ts_enqueued = formatted_body[-1][del_i+1:]
    formatted_body[-1] = formatted_body[-1][:del_i]
    formatted_body.append(float(ts_enqueued)) # last elem is the timestamp of when the message was enqueued
    return formatted_body

# We distribute the queries by batch number, on the all gateway's ports
def attemptDBConnection(batch_num):
    
    PORTS=(9042,9045)
#PORTS=(9042,9043,9044,9045) #DEPLOY
    port_i = batch_num % len(PORTS)
    cluster = Cluster(["172.18.0.1"],port=PORTS[port_i])
    return cluster.connect()


# Stores message from queue to the db
def callback(ch, method, properties, body):

    #PORTS=(9042,9043,9044,9045) #DEPLOY
    PORTS=(9042,9045)
    batch_num = int(float(properties.headers['batch_num']))
    logger.info("Batch %s received" % batch_num)
    
    body = format_batch(dequeue(body))

    ts_enqueued = body[-1]
    body = body[:-1]
    
    BATCH_SIZE = len(body)

    COLUMNS = 'id, vendor_id, pickup_dt, dropoff_dt, passenger_count, trip_distance, rate_code_id, store_and_fwd_flag, pu_location_id, do_location_id, payment_type, fare_amount, extra, mta_tax, tip_amount, tools_amount, improvement_surcharge, total_amount'
    batch = 'BEGIN BATCH\n'
    for i in range(BATCH_SIZE):
        batch += 'INSERT INTO bdp1.runs (' + COLUMNS + ') VALUES (uuid(),%s);\n' % body[i];
    
    batch += 'APPLY BATCH;'
#    print(batch) #Logger check query format
    session = None
    
    while session is None:
        try:
            session = attemptDBConnection(batch_num)
        except NoHostAvailable:
            logger.info("Database (172.18.0.1:%i) still not available, storer waiting 10 seconds..." % PORTS[ batch_num % len(PORTS) ] )
            time.sleep(10)
        else:
            break

    successful_query = False
    while not successful_query:
        try:
            prep_batch = session.prepare(batch)
            session.execute(prep_batch)
        except InvalidRequest:
            logger.info("Keyspace not yet initialized, storer waiting 10 seconds...")
            time.sleep(10)
        else:
            successful_query = True
            ts_now = time.mktime(dt.now().timetuple())
            logger.info("Time needed to ingest batch nr %i was %i seconds" % (batch_num, int(ts_now-ts_enqueued)) )
    
    

# First it takes message from queue

def main():
    credentials = pika.PlainCredentials('user', 'bitnami')
    parameters = pika.ConnectionParameters('172.29.0.1',
                                           5672,
                                           '/',
                                           credentials)
    connection = None
    logger.info("Consumer started, attempting connection with %s." % parameters.host )
    while connection is None:
        try:
            connection = pika.BlockingConnection(parameters)
        except AMQPConnectionError:
            logger.info("Queue still not available, dequeuer waiting 10 seconds...")
            time.sleep(10)
        else:
            logger.info("Connection with queue at %s established." % parameters.host)
            break

    channel = connection.channel()

    channel.queue_declare(queue='taxi-ingest') # we don't know if client.py or consumer.py is run first

    channel.basic_consume(queue='taxi-ingest',
                      auto_ack=True,
                      on_message_callback=callback)

    logger.info(' [*] Waiting for messages. To exit press CTRL+C')

    try:
        channel.start_consuming()
    except ConnectionClosedByBroker:
        logger.warning("Connection with %s closed, restarting..." % parameters.host)
        main()
    except StreamLostError:
        logger.warning("Connection with queue lost, dropping some messages...")
        main()

if __name__ == "__main__":
    main()
