import logging
import sys
from configkeys import ConfigKey
from config import config
from ndp import DockerNdpDaemon

logger = logging.getLogger(__name__)

################
# Main
#############

logging.basicConfig(format=config[ConfigKey.LOGGER_FORMAT])
logging.root.setLevel(config[ConfigKey.LOGGER_LOGLEVEL])

try:
    daemon = DockerNdpDaemon(
        config[ConfigKey.DOCKER_SOCKET_URL],
        config[ConfigKey.HOST_GATEWAY_NETWORK_INTERFACE])

except Exception as ex:
    logger.error("FATAL: {}".format(ex))
    sys.exit(1)
