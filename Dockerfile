# Dockerfile Example for dockerndp-ndp-proxy
FROM        ubuntu:18.04

# Install required packages
RUN         apt-get update \
            && apt-get install -y \
               docker.io \
               git \
               python3-pip \
               sudo
RUN         pip3 install docker

# Download dockerndp-ndp-proxy
WORKDIR     /srv
RUN         git clone https://github.com/pommes/docker-ndp-daemon.git dnd

# Start daemon
WORKDIR      /srv/dnd/app
ENTRYPOINT   ["/usr/bin/python3"]
CMD          ["main.py", "tee", "-a", "/var/log/dnd.log"]