import logging
from docker import DockerClient
import json
import signal
from subprocess import Popen, PIPE
from daemon.exceptions import DaemonException
from daemon.exceptions import DaemonTimeoutException
from urllib3.exceptions import ReadTimeoutError

logger = logging.getLogger(__name__)


class DockerEventDaemon:
    """High level docker client for listening to dockerndp client.

    The class is a wrapper around the :class:`docker.client.DockerClient`
    for use as a daemon.

    It provides:
        * Listeing to dockerndp Events
        * Listening to SIGNALS for safe termination.
    """

    # Properties
    _socket_url = None
    _client = None
    _events = None
    _terminate = False

    # Getters / Setters

    @property
    def socket_url(self):
        return self._socket_url

    @socket_url.setter
    def socket_url(self, val):
        self._socket_url = val

    def __init__(self, socket_url):
        """Creates a new DockerClient.

        :param socket_url: URL to the Docker server.

        Example:
            >>> DockerEventDaemon("unix://var/run/dockerndp.sock")
            >>> DockerEventDaemon("tcp://127.0.0.1:1234")
        """
        assert socket_url, "socket_url not set!"
        signal.signal(signal.SIGINT, self._handle_termination)
        signal.signal(signal.SIGTERM, self._handle_termination)
        self.socket_url = socket_url

        logger.info("Connecting ...")
        self._client = self.init_docker_client()
        if not self._client:
            raise(DaemonException("Unable to connect."))

    def init_docker_client(self):
        """
        :return: the docker client object
        """
        return DockerClient(base_url=self.socket_url)

    # Listens for network connect client and calls handle_network_connect_event
    def listen_network_connect_events(self):
        logger.info("Listening for Events ...")

        try:
            self._events = self._client.events()
            for jsonEvent in self._events:
                event = json.loads(jsonEvent)
                if event['Type'] == 'network' and event['Action'] == 'connect':
                    self._handle_network_connect_event(event)
        except ReadTimeoutError as ex:
            raise DaemonTimeoutException(parent=ex)
        except Exception as ex:
            if self._terminate:
                logger.warning("Error during termination: {}".format(ex))
            else:
                raise DaemonException(parent=ex)

    def shutdown(self):
        """shuts down the daemon."""
        logger.info("Shutting down ...")
        self._terminate = True
        self._events.close()
        self._client.close()

    # Handler for all net work connection client
    def _handle_network_connect_event(self, event: dict):
        pass

    # Shutdown app (Param _ (frame) is not needed.
    def _handle_termination(self, signum, _):
        logger.info("Signal '{}' received.".format(signum))
        self.shutdown()

    # Fetches IPv6 address
    @staticmethod
    def fetch_ipv6_address(container) -> (int, str, str):
        """Extracts the ipv6 address of a container.

        Since :class:`docker.DockerClient` does not have the ability to read the IPv6 address
        of a container this method retrieves it with calling the *docker* binary as a sub process.

        :param container: The container from which the
        :return: Tuple (Returncode, IPv6 address, STDERR if Returncode is not 0)
        """
        process = Popen([
            "docker",
            "container",
            "inspect",
            "--format={{range .NetworkSettings.Networks}}{{.GlobalIPv6Address}}{{end}}",
            container.id],
            stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        stdout = stdout.decode('utf-8').rstrip() if stdout else ""
        stdout = stdout if stdout else None
        stderr = stderr.decode('utf-8').rstrip() if stderr else ""
        stderr = stderr if stderr else None
        return process.returncode, stdout, stderr
