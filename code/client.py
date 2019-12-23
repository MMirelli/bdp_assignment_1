import pika
from pika.exceptions import AMQPConnectionError

import argparse
import csv

from datetime import datetime as dt
import time
import logging
import threading


logger = logging.getLogger("client")
logger.setLevel(logging.INFO)

def enqueue(th_id, body, batch_num):
    
    credentials = pika.PlainCredentials('user', 'bitnami')
    parameters = pika.ConnectionParameters('172.29.0.4',
                                           5672,
                                           '/',
                                           credentials)
    connection = None
    while connection is None:
        try:
            connection = pika.BlockingConnection(parameters)
        except AMQPConnectionError:
            logger.warning("[Thread %i]" % th_id + " Queue still not available, enqueuer waiting 10 seconds...")
            time.sleep(10)
        else:
            logger.info("[Thread %i]" % th_id + " Connection with queue at %s established." % parameters.host)
            break

    channel = connection.channel()
    channel.queue_declare(queue='taxi-ingest')
    channel.basic_publish(exchange='',
                          routing_key='taxi-ingest',
                          body=body,
                          properties=pika.BasicProperties(
                              headers={"batch_num":str(batch_num)} ))
    logger.debug("[Thread %i]" % th_id + " [x] Sent " + body)
    connection.close()

def prepare_and_enqueue(batch, line_count, batch_size, th_id):
    ts_now = str(time.mktime(dt.now().timetuple()))
    # computes current time to observe ingestion rate
    
    body = ';'.join(batch)
    logger.warning("[Thread %i]" % th_id +
                     " Enqueuing batch nr %i"
                     % int(line_count / batch_size) )
    enqueue(th_id, body + "|" + ts_now, int(line_count / batch_size))


def thread_main(th_id, filename='data_0.csv',batch_size=10, data_amount=1000):

    logger.info("[Thread %i] Client started; opening %s" % (th_id, filename))
    batch = []
    line_count = 0
    with open('../data/'+filename) as readData:
        csv_reader = csv.reader(readData, delimiter=',')
        for row in csv_reader: # read a row as {column1: value1, column2: value2,...}
            if line_count != 0:

                batch.append(','.join(row))
                if line_count % batch_size ==  0:
                    prepare_and_enqueue(batch,line_count,batch_size,th_id)
                    batch = []
                
                if line_count == data_amount: break
                
            line_count += 1
    # in the case batch_size doesn't divide data_amount
    if len(batch) != 0:
        prepare_and_enqueue(batch, (line_count + batch_size), batch_size, th_id)


def main():
    MAX_FILE_NUMBER = 1
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', help='size of the batch', default='10')
    parser.add_argument('--clients', help='number of concurrent clients', default='10')
    parser.add_argument('--data', help='number of rows to ingest', default='100')
    
    args = parser.parse_args()
    
    n_clients = int(args.clients)
    batch_size = int(args.batch)
    n_rows = int(args.data)

    
    logging.getLogger("pika").setLevel(logging.CRITICAL)
    format = "client | %(asctime)s >> %(message)s"
    logging.basicConfig(format=format, datefmt="%H:%M:%S",
                        filename='../logs/client/client_' + str(n_clients) + '.log')

    
    logger.info("[Main] starting %i threads with %i batch size" % (n_clients, batch_size))

    threads = []
    for i in range(1, n_clients+1 ):
        cur_t = threading.Thread(
            target=thread_main,
            args =(i, "data_%i.csv" % (i % MAX_FILE_NUMBER + 1) , batch_size, n_rows))
        threads.append(cur_t)
        cur_t.start()

    for thread in threads:
        thread.join()

    logger.info("Clients have terminated")
        
if __name__ == "__main__":
    main()



