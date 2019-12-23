# BDP - Assignment 1

## Overview

In this assignment we simulate ingestion of the dataset [2018 Yellow Taxi Trip Data](https://data.cityofnewyork.us/Transportation/2018-Yellow-Taxi-Trip-Data/t29m-gskq) into a cassandra cluster, (`mysimbdp-coredms`). The application manages to serve several users at a time (we have tested it with up to 500 concurrent users), with no data loss, thanks to the RabbitMQ cluster employed.

Here is the platform design:

![](design.jpg)

-----

## Project Structure

```
code
├── client.py
├── db
│   ├── docker-compose.yml
│   └── setuppers
│       ├── Dockerfile
│       └── setup_db.py
├── install_dependencies.sh
├── queue
│   ├── consumer.py
│   ├── docker-compose.yml
│   └── Dockerfile
├── README.md
├── run.sh
├── start_db.sh
├── start_queue.sh
└── utils
    ├── Dockerfile
    └── split_data.py
```

The deploy uses docker-compose for starting up 2 `cassandra-db` and 2 `bitnami/rabbitmq` containerised nodes. Other two components use containers as well:

* the program setting up the database keyspace ([`setup_db`](code/db/setuppers/setup_db.py), [`code/db/setuppers/Dockerfile`](code/db/setuppers/Dockerfile));
* the program in charge of dequeuing the messages forwarded to the RabbitMQ cluster ([`consumer`](code/queue/consumer.py), [`code/queue/Dockerfile`](code/queue/Dockerfile)).

 both are pre-built on top of a docker image of python3 with cassandra-python as a dependency (in [`code/utils/Dockerfile`](code/utils/Dockerfile)), which I pushed to my docker repository so that it is automatically downloaded when composing.
 
The main building program is started by [`run`](code/run.sh), which triggers the composition of the docker-compose files ([`code/db/docker-compose.yml`](code/db/docker-compose.yml) and [`code/queue/docker-compose.yml`](code/queue/docker-compose.yml)) and then a number of clients ([`client.py`](code/client.py)) specified by the user. 

Logs can be found in `logs` with each file following the format: `<log_type>_<client_number>.log`, where `log_type` is one of `db`, `queue`, `client` and `client_number` is the number of concurrent clients run for the ingestion. 

-----
