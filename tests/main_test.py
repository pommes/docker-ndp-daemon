import unittest
import mock
import config
import logging
import main

logger = logging.getLogger(__name__)
logging.basicConfig(format=config.logger.format)
logging.root.setLevel(config.logger.level)


def side_effect_value_error():
    def raise_error():
        raise ValueError("Test error raised!")
    return raise_error()


class MainTest(unittest.TestCase):

    def setUp(self):
        """Sets _daemon with mocked :class:`DockerClient``
        """

    @mock.patch('daemon.DockerNdpDaemon')
    def test_main__ok(self, mock_docker_ndp_daemon):
        main.init_app()
        self.assertTrue(mock_docker_ndp_daemon.called)

    @mock.patch('daemon.DockerNdpDaemon', side_effect=side_effect_value_error)
    @mock.patch('sys.exit')
    def test_main__fail_exception_raised(self, mock_sys_exit, mock_docker_ndp_daemon):
        main.init_app()
        self.assertTrue(mock_docker_ndp_daemon.called)
        self.assertTrue(mock_sys_exit.called)


if __name__ == '__main__':
    unittest.main()
