import logging
from .events import DockerEventDaemon
from .exceptions import DaemonException
from subprocess import Popen, PIPE

logger = logging.getLogger(__name__)


class DockerNdpDaemon(DockerEventDaemon):
    """A special :class:`DockerEventDaemon` that adds IPv6 addresses of
    recently started docker containers to the NDP proxy for
    getting IPv6 internet connectivity.
    """
    _ethernet_interface = None

    def __init__(self, socket_url, ethernet_interface):
        """ Creates a new instance.

        :param (str) socket_url: Path of the dockerndp socket file.
        :param (str) ethernet_interface: Name of the ethernet interface that is an internet gateway.
        """
        super().__init__(socket_url)
        self._ethernet_interface = ethernet_interface

        rval, cmd, stderr = self._activate_ndp_proxy()
        if rval != 0:
            raise (DaemonException("{} returned with code '{}': '{}'".format(cmd, rval, stderr)))

        self._add_all_existing_containers_to_neigh_proxy()
        self.listen_network_connect_events()

    def _handle_network_connect_event(self, event):
        # Fetches Container from id in event
        container_id = event['Actor']['Attributes']['container']
        container = self._client.containers.get(container_id)
        logger.debug("Event: Container '{}' connected to dockerndp network."
                     .format(container.name))
        self._add_container_to_ipv6_ndp_proxy(container)

    def _add_container_to_ipv6_ndp_proxy(self, container):
        ipv6_address = self._try_fetch_ipv6_address(container)
        if not ipv6_address:
            logger.info("Ignoring container '{}'. It has no IPv6 address.".format(container.name))
            return

        rval, cmd, stderr = self._add_ipv6_neigh_proxy(ipv6_address)
        if rval != 0:
            raise (DaemonException("{} returned with code '{}': '{}'".format(cmd, rval, stderr)))

        logger.info("Setting IPv6 ndp proxy for container '{}': '{}'".format(container.name, cmd))

    @staticmethod
    def _try_fetch_ipv6_address(container):
        # Adds the passed container to the ipv6 neighbour discovery proxy
        rval, ipv6_address, stderr = DockerNdpDaemon.fetch_ipv6_address(container)
        if rval != 0:
            raise (DaemonException("Fetching IPv6 address for container '{}' returned with code '{}': '{}'"
                   .format(container.name, rval, stderr)))

        if not ipv6_address:
            return None

        logger.debug("Event: Container '{}' connected to dockerndp network has IPv6 address '{}'."
                     .format(container.name, ipv6_address))
        return ipv6_address

    def _add_ipv6_neigh_proxy(self, ipv6_address) -> (int, str, str):
        # Sets IPv6 neighbour discovery to ethernet interface.
        cmd = "sudo ip -6 neigh add proxy {} dev {}".format(ipv6_address, self._ethernet_interface)
        process = Popen(cmd.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)

        stdout, stderr = process.communicate()
        stderr = stderr.decode('utf-8').rstrip() if stderr else ""
        stderr = stderr if stderr else None
        return process.returncode, cmd, stderr

    def _activate_ndp_proxy(self) -> (int, str, str):
        # Activates the ndp proxy
        logger.info("Activating IPv6 ndp proxy on '{}' ...".format(self._ethernet_interface))
        cmd = "sudo sysctl net.ipv6.conf.{}.proxy_ndp=1".format(self._ethernet_interface)
        process = Popen(cmd.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)

        stdout, stderr = process.communicate()
        stderr = stderr.decode('utf-8').rstrip() if stderr else ""
        stderr = stderr if stderr else None
        return process.returncode, cmd, stderr

    def _add_all_existing_containers_to_neigh_proxy(self):
        # Adds all running containers to the IPv6 neighbour discovery proxy
        logger.info("Adding all runnning containers to IPv6 ndp proxy...")
        for container in self._client.containers.list():
            self._add_container_to_ipv6_ndp_proxy(container)
