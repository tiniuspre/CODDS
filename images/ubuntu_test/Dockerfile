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
