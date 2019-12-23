# Starts the db environment

NETWORK_NAME=casnet
if [ -z $(docker network ls --filter name=^${NETWORK_NAME} --format="{{ .Name }}") ] ; then 
    # stops any container in the docker compose
    docker-compose -f db/docker-compose.yml down 2> /dev/null
    # removes any cassandra service, linked to the previous setup  
    docker rm $(docker container ls -a | grep cas) 2> /dev/null
    # creates another network, managed externally
    docker network create --gateway 172.18.0.1 --subnet 172.18.0.0/28 ${NETWORK_NAME}
fi

docker-compose -f db/docker-compose.yml up 
