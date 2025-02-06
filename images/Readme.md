# Docker images

The program automatically detects new folders inside the images directory. The folder name is the name of the image. It looks for the config.json file so it knows what to do.

### Adding
```bash
mkdir new_image # Change with image name
```

Then create a Dockerfile in the new_image directory.

```bash
cd new_image
touch new_image/Dockerfile
touch new_image/config.json 
```


Then insert code into the Dockerfile.


Configuration.
The config.json works alot like a docker-compose file. It contains the information about each image and how it should be run.

Available fields:
info:
- challenge_name: The name of the challenge
- challenge_description: The description of the challenge
- connection_type: The type of connection. http / tcp / ssh ... (http is the only working for now)
- connection_port (int): The port the image is running on
- challenge_pin (str): A pin that is required to access the challenge. Needs to be exactly 8 characters long.
- processs: The processs that is running on the image
    - dockerfile: The path to the Dockerfile
    - environment: The environment variables that should be set
    - exposed_ports: The ports that should be exposed


When you create several processes in the config.json file, a network is automatically created between the containers. This means that the containers can communicate with each other.

Example config file with multiple images
```json
{
  "info": {
    "challenge_name": "Visitor CTF test",
    "challenge_description": "This is a test challenge",
    "connection_type": "http",
    "connection_port": 80
  },
  "processes": {
    "internal": {
      "dockerfile": "internal-server/Dockerfile",
      "environment": {
        "flag": "CTF{test_flag}"
      }
    },
    "visitor": {
      "dockerfile": "visitor-bot/Dockerfile",
            "environment": {
        "flag": "CTF{test_flag}"
      },
        "exposed_ports": [
    {
      "port": 80,
      "protocol": "tcp"
    }
  ]
    }
  }
}
```

Example Dockerfile & Config for ubuntu with web ssh.

Dockerfile
```Dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y curl && apt install sudo

RUN useradd -m -s /bin/bash ctfuser && \
    echo 'ctfuser:hemmelig' | chpasswd && \
    adduser ctfuser sudo


RUN apt install -y nodejs && apt install -y npm

RUN npm install -g wetty@2.5.0
EXPOSE 80

CMD ["wetty", "--port", "80", "--ssh-port", "22", "--base", "/", "--ssh-host", "localhost"]
```

config.json
```json
{
  "info": {
    "challenge_name": "Ubuntu web ssh",
    "challenge_description": "This is a test challenge",
    "challenge_pin": "24682468",
    "connection_type": "ssh",
    "connection_port": 80,
    "username": "bruker",
    "password": "hemmelig"
  },
  "processes": {
    "ubuntu": {
      "dockerfile": "Dockerfile",
      "environment": {
        "flag": "CTF{test_flag}",
        "SSH_PASSWORD": "hemmelig"
      },
  "exposed_ports": [
    {
      "port": 80,
      "protocol": "tcp"
    }
  ]
    }
  }
}
```
