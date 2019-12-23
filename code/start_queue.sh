# Starts the RabbitMQ environment

NETWORK_NAME=rmqnet
if [ -z $(docker network ls --filter name=^${NETWORK_NAME} --format="{{ .Name }}") ] ; then 
    # stops any container in the docker compose
    docker-compose -f queue/docker-compose.yml down 2> /dev/null
    # removes any cassandra service, linked to the previous setup  
    docker rm $(docker container ls  | grep -E 'stats|queue') 2> /dev/null
    # creates another network, managed externally
    docker network create --gateway 172.29.0.1 --subnet 172.29.0.4/29 ${NETWORK_NAME}
fi

docker-compose -f queue/docker-compose.yml up
