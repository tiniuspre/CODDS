# Ctf On Demand Docker System
#### Codds
###### Author: Tinius Presterud

### [Live demo](https://ctf.tinius.dev)
### [Images showcase](showcase/Readme.md)
### [Frontend repo](https://github.com/tiniuspre/codds_frontend)

## Description
This is a web backend application that has the capability to spawn on demand docker containers.

It is created for Capture The Flag events (CTF's) where the users needs to have their own container. Example a web application where they need to mess with the database or get root access to the system.

## About
The backend contains three main parts:
1. Django web server
2. Docker container manager
3. Træfik reverse proxy


## Django web server

### Authentication
The users can create and login to their accounts using discord login.

### System
The system app is the "logical" part of the program. Here the endpoints for creating and managing the containers are located.

### Admin_app
Admin stuff


## Docker container manager
```docker_manager.py``` is the main file for managing the docker containers.

```images/``` is the directory where the docker images are stored.
```images/program_handler.py``` is the file that handles the images.

[Images docs](images/Readme.md)


## Træfik
Træfik is a reverse proxy that is used to route the traffic to the correct container.


## Setup

### Discord setup
DISCORD_REDIRECT_URI needs to be the same as the backend domain.

Example if backend domain is ```backend-ctf.tinius.dev```
The redirect url needs to be ```https://backend-ctf.tinius.dev/accounts/discord/```

## Installation, Config & Running
1. Clone the repository
2. Setup discord bot [here](https://discord.com/developers/applications/)
3. Configure the ```.env``` file.
4. Update the certificates in ```certs/``` with your own certificates. ```certs/priv.key``` and ```certs/pub.crt```
5. Update the line ``` - "traefik.http.routers.ctf_app.rule=Host(`backend-ctf.tinius.dev`)"``` in
 ```docker-compose.yml``` needs to be the same domain as in the .env file for backend.
6. Add wildcard to your domain. Example ```backend-ctf.tinius.dev``` and ```*.backend-ctf.tinius.dev```

### Adding images
Check out [Images docs](images/Readme.md)

### Running
It may take some time before the backend is up as it has to build the images.
```bash
docker compose build --no-cache
docker compose up -d
```

### Stopping
Gracefull shutdown has not been implemented yet. So you have to stop the containers manually if you kil the docker compose.
```bash
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker network rm $(docker network ls -q)
docker rmi $(docker images -q)
```

## TODOs
1. Add ability to pull and use images directly from docker hub