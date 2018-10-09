import logging
from config_enum import ConfigEnum


# Change config variables for your needs
config = {
    # The internet gateway network interface of your server
    ConfigEnum.HOST_GATEWAY_NETWORK_INTERFACE: "eth0",
    # The docker socket file
    ConfigEnum.DOCKER_SOCKET_FILE: "unix://var/run/docker.sock",
    # The output format of the logger
    ConfigEnum.LOGGER_FORMAT: "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    # Logging output is this level or higher - DEBUG (lowest), INFO, WARN, ERROR (highest)
    ConfigEnum.LOGGER_LOGLEVEL: logging.DEBUG
}

