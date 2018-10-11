if __name__ == "__main__":
    import sys
    import logging
    from daemon import DockerNdpDaemon

    logger = logging.getLogger(__name__)

    try:
        import config

        logging.basicConfig(format=config.logger.format)
        logging.root.setLevel(config.logger.level)

        daemon = DockerNdpDaemon(
            config.docker.socket,
            config.host.gateway)

    except Exception as ex:
        logger.critical("CRITICAL: {}".format(ex))
        sys.exit(1)
else:
    raise ImportError("Run this file directly, don't import it!")
