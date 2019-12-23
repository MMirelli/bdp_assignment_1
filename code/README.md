# Deployment report

## Deployment testing

This deployment has been tested on `5.2.11-1-MANJARO` (Linux) and `18.04.1-Ubuntu`;

## Requirements

The following software is required to run the project:

* `bash`; 
* [`docker`](https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-docker-engine---community-1);
* [`docker-compose`](https://docs.docker.com/compose/install/);
* `python`(3);
* `pip`(3);
* [`pika`](https://pypi.org/project/pika/) for python.

The following steps must be followed in order to run the project correctly:

```bash 
./install_dependencies
```

```bash 
./run.sh <n_clients> 
```

> *Note*: the last command might ovewrite the previously generated logs.
