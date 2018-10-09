import logging
import docker
import json
import signal

logger = logging.getLogger(__name__)


class DockerClient:

    # Properties
    _socket_file = None
    _client = None
    _events = None
    _terminate = False

    # Getters / Setters

    @property
    def socket_file(self):
        return self._socket_file

    @socket_file.setter
    def socket_file(self, val):
        self._socket_file = val

    # Constructor
    def __init__(self, socket_file):
        assert socket_file, "socket_file not set!"
        signal.signal(signal.SIGINT, self._handle_termination)
        signal.signal(signal.SIGTERM, self._handle_termination)
        self._socket_file = socket_file

        logger.info("Connecting ...")
        self._client = docker.from_env()
        if not self._client:
            self._client = docker.DockerClient(base_url=self._socket_file)
            if not self._client:
                raise(ValueError("Unable to connect."))

    # Listens for network connect events and calls handle_network_connect_event
    def listen_network_connect_events(self):
        logger.info("Listening for Events ...")

        try:
            self._events = self._client.events()
            for jsonEvent in self._events:
                event = json.loads(jsonEvent)
                if event['Type'] == 'network' and event['Action'] == 'connect':
                    try:
                        self._handle_network_connect_event(event)
                    except Exception as ex:
                        logger.error("Error during event processing: {}".format(ex))

        except Exception as ex:
            if self._terminate:
                logger.warning("Error during termination: {}".format(ex))
            else:
                raise ex

    # Handler for all net work connection events
    def _handle_network_connect_event(self, event):
        pass

    # Shut
    def _handle_termination(self, signum, frame):
        logger.info("Signal '{}' received. Shutting down ...".format(signum))
        self._terminate = True
        self._events.close()
        self._client.close()

