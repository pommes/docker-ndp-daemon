from enum import Enum


class ConfigEnum(Enum):
    HOST_GATEWAY_NETWORK_INTERFACE = "host.gateway_network_interface",
    DOCKER_SOCKET_FILE = "docker.socket_file",
    LOGGER_FORMAT = "logger.format",
    LOGGER_LOGLEVEL = "logger.loglevel"
