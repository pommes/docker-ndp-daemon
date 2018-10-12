import unittest
import mock
import logging
from docker import DockerClient
from docker.errors import DockerException
from subprocess import Popen
import signal
from daemon.events import DockerEventDaemon
import config

logger = logging.getLogger(__name__)
logging.basicConfig(format=config.logger.format)
logging.root.setLevel(config.logger.level)


def error_during_terminate():
    def raise_error():
        raise ValueError("Test error during termination...")
    return raise_error()


class DockerEventDaemonTest(unittest.TestCase):

    def setUp(self):
        """Sets _daemon with mocked :class:`DockerClient``
        """
        with mock.patch.object(DockerClient, '__init__', return_value=None):
            self._daemon = DockerEventDaemon("socket")

    @mock.patch.object(DockerClient, '__init__')
    def test_init__ok(self, mock_docker_client):
        """Tests if DockerEventDaemon instance is created properly.

        :param mock_docker_client: DockerClient is mocked to avoid testing with real socket.
        """
        mock_docker_client.return_value = None
        daemon = DockerEventDaemon("socket")
        self.assertIsNotNone(daemon)
        mock_docker_client.assert_called_with(base_url='socket')

    def test_init__fail__file_not_found(self,):
        try:
            DockerEventDaemon("socket")
        except DockerException as ex:
            logger.info("{}: {}".format(ex.__class__, ex))
            return

        self.fail("DockerException expected.")

    @mock.patch.object(DockerEventDaemon, 'init_docker_client', mock.Mock(return_value=None))
    def test_init__fail__docker_client_is_none(self):
        try:
            DockerEventDaemon("socket")
        except ValueError as ex:
            logger.info("{}: {}".format(ex.__class__, ex))
            return

        self.fail("ValueError expected.")

    @mock.patch.object(DockerClient, 'events')
    @mock.patch.object(DockerEventDaemon, '_handle_network_connect_event')
    def test_listen_network_connect_events__ok(self, mock_event_handler, mock_events):
        mock_events.return_value = [
            '{"Type":"network","Action":"connect","Actor":{"ID":"29985997bf53d5933fea12ac6c40ccd6240013b88f940270bfd1d16a0f5fb5bd","Attributes":{"container":"534280333f1f64f7cfeb56dde3a76788b2961abc807b3833705fa2d4fcee2f40","name":"bridge","type":"bridge"}},"scope":"local","time":1539202002,"timeNano":1539202002835354153}',
            '{"Type":"network","Action":"disconnect","Actor":{"ID":"29985997bf53d5933fea12ac6c40ccd6240013b88f940270bfd1d16a0f5fb5bd","Attributes":{"container":"3fc260a2e5a99df767b6ebfe0506d598b7502d1be38f82dc5513dcd25bc62c12","name":"bridge","type":"bridge"}},"scope":"local","time":1539202263,"timeNano":1539202263993893537}',
            '{"Type":"network","Action":"connect","Actor":{"ID":"29985997bf53d5933fea12ac6c40ccd6240013b88f940270bfd1d16a0f5fb5bd","Attributes":{"container":"534280333f1f64f7cfeb56dde3a76788b2961abc807b3833705fa2d4fcee2f40","name":"bridge","type":"bridge"}},"scope":"local","time":1539202002,"timeNano":1539202002835354153}'
        ]
        mock_event_handler.return_value = 42
        self._daemon.listen_network_connect_events()

        self.assertTrue(mock_events.called)
        self.assertTrue(mock_event_handler.called)
        self.assertEqual(2, mock_event_handler.call_count,
                         "Only 2 of the 3 client are of Type 'network' and Action 'connect'.)")

    @mock.patch.object(DockerClient, 'events', side_effect=error_during_terminate)
    def test_listen_network_connect_events__fail(self, mock_events):
        try:
            self._daemon.listen_network_connect_events()
            self.fail("Exception expected.")
        except ValueError:
            pass

    @mock.patch('docker.models.containers.Container')
    @mock.patch.object(Popen, "communicate",
                       return_value=(bytearray("\n", "utf-8"), bytearray("Some Error occured\n", "utf-8"), ))
    def test_fetch_ipv6_address__ok_return_1(self, mock_communicate, mock_container):
        mock_container.id = "42"
        returncode, ipv6_address, stderr = DockerEventDaemon.fetch_ipv6_address(mock_container)
        #self.assertEqual(1, returncode)
        self.assertIsNone(ipv6_address)
        self.assertEqual("Some Error occured", stderr)

    @mock.patch('docker.models.containers.Container')
    @mock.patch.object(Popen, 'communicate', return_value=(bytearray("fe80::1\n", "utf-8"), bytearray("\n", "utf-8")))
    def test_fetch_ipv6_address__ok(self, mock_communicate, mock_container):
        mock_container.id = "42"
        returncode, ipv6_address, stderr = DockerEventDaemon.fetch_ipv6_address(mock_container)
        # self.assertEqual(0, returncode)
        self.assertEqual("fe80::1", ipv6_address)
        self.assertIsNone(stderr)
        self.assertTrue(mock_communicate.called)

    @mock.patch.object(DockerClient, "events")
    @mock.patch.object(DockerClient, "close")
    def test_handle_termination__ok(self, mock_close, mock_events):
        signals = [signal.SIGTERM, signal.SIGINT]
        for curr_signal in signals:
            with self.subTest():
                self._daemon.listen_network_connect_events()
                self._daemon._handle_termination(curr_signal, None)

                self.assertTrue(mock_events.called)
                self.assertTrue(mock_close.called)
                self.assertTrue(self._daemon._terminate)


if __name__ == '__main__':
    unittest.main()
