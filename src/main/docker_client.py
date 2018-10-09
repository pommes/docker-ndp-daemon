import logging
import docker
import json

logger = logging.getLogger(__name__)


class DockerClient:

    # Properties
    _socket_file = None
    _client = None

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

        for jsonEvent in self._client.events():
            event = json.loads(jsonEvent)
            if event['Type'] == 'network' and event['Action'] == 'connect':
                self._handle_network_connect_event(event)

    # Handler for all net work connection events
    def _handle_network_connect_event(self, event):
        pass
