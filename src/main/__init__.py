import logging
from config_enum import ConfigEnum
from config import config
from docker_ndp_proxy import DockerIpv6NeighbourDiscoverer

logger = logging.getLogger(__name__)

################
# Main
#############

logging.basicConfig(format=config[ConfigEnum.LOGGER_FORMAT])
logging.root.setLevel(config[ConfigEnum.LOGGER_LOGLEVEL])

try:
    docker_client = DockerIpv6NeighbourDiscoverer(
        config[ConfigEnum.DOCKER_SOCKET_FILE],
        config[ConfigEnum.HOST_GATEWAY_NETWORK_INTERFACE])

except Exception as ex:
    logger.error("FATAL: {}".format(ex))
