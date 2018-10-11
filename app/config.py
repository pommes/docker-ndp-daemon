import logging
import configparser

log = logging.getLogger(__name__)


class Config(dict):
    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)
        self.__dict__ = self


loglevel_map = {'critical': logging.CRITICAL,
                'fatal': logging.FATAL,
                'error': logging.ERROR,
                'warning': logging.WARNING,
                'warn': logging.WARNING,
                'info': logging.INFO,
                'debug': logging.DEBUG
                }
config_file = "../dnd.ini"

conf = configparser.ConfigParser()
successful_files = conf.read(config_file)
if not successful_files:
    open(config_file)  # Raises error if not found
    raise ImportError("The config file '{}' was found but could not be parsed.".format(config_file))

try:
    # Create sections with attributes
    host = Config(conf['host'])
    docker = Config(conf['docker'])
    logger = Config(conf['logger'])
except Exception as ex:
    raise ImportError("The config file '{}' was found but section {} is missing.".format(config_file, ex))

logger.level = loglevel_map[logger.level.lower()]




