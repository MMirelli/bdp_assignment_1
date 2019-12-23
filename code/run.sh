# $1 clients
# $2 timeout, before shutting down compose

CLIENTS=$1
if [ z $CLIENTS ]; then
    CLIENTS=10
fi

TIMEOUT=$2
if [ z $TIMEOUT ]; then
    TIMEOUT=5
fi

# starts the db environment
./start_db.sh > '../logs/db/db_'$CLIENTS'.log' &

sleep 60
echo 'Cassandra cluster ready'

# starts rabbitMQ clusters 
./start_queue.sh > '../logs/queue/queue_'$CLIENTS'.log' &

sleep 40
echo 'RabbitMQ cluster ready'

echo 'Starting '$CLIENTS' clients'

python client.py --batch=15 --clients=$CLIENTS --data=100 > '../logs/client/client_'$CLIENTS'.log' &

sleep $TIMEOUT'm'

docker-compose -f db/docker-compose.yml down

docker-compose -f queue/docker-compose.yml down

echo 'Program terminated, outputs stored in ../logs'
