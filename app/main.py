def init_app():
    import sys
    import logging
    from daemon import DockerNdpDaemon
    from urllib3.exceptions import ReadTimeoutError

    logger = logging.getLogger(__name__)
    daemon = None

    try:
        import config

        logging.basicConfig(format=config.logger.format)
        logging.root.setLevel(config.logger.level)

        daemon = DockerNdpDaemon(
            config.docker.socket,
            config.host.gateway)

    except ReadTimeoutError as ex:
        logger.debug(ex)
        logger.info("Docker connection read timed out. Reconnecting ...")
        if daemon:
            daemon.shutdown()
        init_app()
        return()

    except Exception as ex:
        logger.critical("CRITICAL: {}".format(ex))
        sys.exit(1)


if __name__ == "__main__":
    init_app()

