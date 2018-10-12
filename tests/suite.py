import unittest
from events_test import DockerEventDaemonTest
from ndp_test import DockerNdpDaemonTest
from main_test import MainTest


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MainTest))
    suite.addTest(unittest.makeSuite(DockerEventDaemonTest))
    suite.addTest(unittest.makeSuite(DockerNdpDaemonTest))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
