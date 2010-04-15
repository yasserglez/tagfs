# -*- coding: utf-8 -*-

"""
Pruebas por unidad del Sistema.   
"""

import os
import unittest
import threading

from tagfs.server import TagFSServer
from tagfs.client import TagFSClient


SRC_DIR = os.path.join(os.path.dirname(__file__), os.pardir)

TESTS_DIR = os.path.abspath(os.path.join(SRC_DIR, 'tests'))

DATA_DIR = os.path.abspath(os.path.join(TESTS_DIR, 'data'))

SERVER_DATA_DIR = os.path.abspath(os.path.join(DATA_DIR, 'server'))

CLIENT_DATA_DIR = os.path.abspath(os.path.join(DATA_DIR, 'client'))

SERVER_INTERFACE = "127.0.0.1"

CLIENT_INTERFACE = "127.0.0.1"

SERVER_COUNT = 5

SERVER_CAPACITY = 1073741824

FILES_COUNT = 10

MAX_FILE_CAPACITY = 1073741


class Test(unittest.TestCase):
    """
    Pruebas por unidad del Sistema.   
    """

    def setUp(self):
        """
        Inicializa un ambiente para realizar las pruebas.
        """
        servers = []
        threads = []
        clients = []
        path = os.path.abspath(os.path.join(SERVER_DATA_DIR, "server_{number}"))
        for i in xrange(SERVER_COUNT):
            # Starting the servers.
            server_data = path.format(number = i)
            os.mkdir(path)
            server = TagFSServer(SERVER_INTERFACE, server_data, SERVER_CAPACITY)
            servers.append(server)
            # Starting the threads.
            thread = threading.Thread(server.start)
            thread.start()
            threads.append(thread)
        # Starting the client.
        client = TagFSClient(CLIENT_INTERFACE)
        self._servers = servers
        self._threads = threads
        self._client = client
        
    def tearDown(self):
        """
        Termina el ambiente creado para realizar las pruebas. 
        """
        for server in self._servers:
            server.stop()
        for thread in self._threads:
            thread.join()
        self._client.terminate()

    def testName(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()