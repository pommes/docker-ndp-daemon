from enum import Enum


class ConfigKey(Enum):
    HOST_GATEWAY_NETWORK_INTERFACE = "host.gateway_network_interface",
    DOCKER_SOCKET_URL = "dockerndp.socket_file",
    LOGGER_FORMAT = "logger.format",
    LOGGER_LOGLEVEL = "logger.loglevel"
