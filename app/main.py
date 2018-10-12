def main():
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


if __name__ == "__main__":
    main()

