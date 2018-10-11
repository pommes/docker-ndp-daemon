import logging
from events import DockerEventDaemon
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
            raise (ValueError("{} returned with code '{}': '{}'".format(cmd, rval, stderr)))

        self._add_all_existing_containers_to_neigh_proxy()
        self.listen_network_connect_events()

    # Fetches Container from id in event
    def _handle_network_connect_event(self, event):
        container_id = event['Actor']['Attributes']['container']
        container = self._client.containers.get(container_id)
        logger.debug("Event: Container '{}' connected to dockerndp network."
                     .format(container.name))
        self._add_container_to_neigh_proxy(container)

    # Adds the passed container to the ipv6 neighbour discovery proxy
    def _add_container_to_neigh_proxy(self, container):
        rval, ipv6_address, stderr = self.fetch_ipv6_address(container)
        if rval != 0:
            raise (ValueError("Fetching IPv6 address for container '{}' returned with code '{}': '{}'"
                   .format(container.name, rval, stderr)))

        if not ipv6_address:
            logger.info("Ignoring container '{}'. It has no IPv6 address.".format(container.name))
            return

        logger.debug("Event: Container '{}' connected to dockerndp network has IPv6 address '{}'."
                     .format(container.name, ipv6_address))

        rval, cmd, stderr = self._add_ipv6_neigh_proxy(ipv6_address)
        if rval != 0:
            raise (ValueError("{} returned with code '{}': '{}'".format(cmd, rval, stderr)))

        logger.info("Setting IPv6 ndp proxy for container '{}': '{}'".format(container.name, cmd))

    # Sets IPv6 neighbour discovery to ethernet interface.
    def _add_ipv6_neigh_proxy(self, ipv6_address) -> (int, str, str):
        cmd = "sudo ip -6 neigh add proxy {} dev {}".format(ipv6_address, self._ethernet_interface)
        process = Popen(cmd.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)

        stdout, stderr = process.communicate()
        stderr = stderr.decode('utf-8').rstrip() if stderr else None
        return process.returncode, cmd, stderr

    # Activates the ndp proxy
    def _activate_ndp_proxy(self) -> (int, str, str):
        logger.info("Activating IPv6 ndp proxy on '{}' ...".format(self._ethernet_interface))
        cmd = "sudo sysctl net.ipv6.conf.{}.proxy_ndp=1".format(self._ethernet_interface)
        process = Popen(cmd.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)

        stdout, stderr = process.communicate()
        stderr = stderr.decode('utf-8').rstrip() if stderr else None
        return process.returncode, cmd, stderr

    # Adds all running containers to the IPv6 neighbour discovery proxy
    def _add_all_existing_containers_to_neigh_proxy(self):
        logger.info("Adding all runnning containers to IPv6 ndp proxy...")
        for container in self._client.containers.list():
            self._add_container_to_neigh_proxy(container)