import logging
from configkeys import ConfigKey


# Change config variables for your needs
config = {
    # The internet gateway network interface of your server
    ConfigKey.HOST_GATEWAY_NETWORK_INTERFACE: "eth0",
    # The dockerndp socket file
    ConfigKey.DOCKER_SOCKET_URL: "unix://var/run/docker.sock",
    # The output format of the logger
    ConfigKey.LOGGER_FORMAT: "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    # Logging output is this level or higher - DEBUG (lowest), INFO, WARN, ERROR (highest)
    ConfigKey.LOGGER_LOGLEVEL: logging.INFO
}

