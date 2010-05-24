# -*- coding: utf-8 -*-

"""
Pruebas por unidad del Sistema.   
"""

import os
import sys
import time
import unittest
import threading
import shutil

# Add to the Python path the directory containing the packages in the source distribution. 
SRC_DIR = os.path.join(os.path.dirname(__file__), os.pardir)
PACKAGES_DIR = os.path.abspath(os.path.join(SRC_DIR, 'packages'))
sys.path.insert(0, PACKAGES_DIR)

# Add the contrib directory to the Python path.
CONTRIB_DIR = os.path.abspath(os.path.join(PACKAGES_DIR, 'tagfs', 'contrib'))
sys.path.insert(0, CONTRIB_DIR)

from tagfs.client import TagFSClient


TESTS_DIR = os.path.abspath(os.path.join(SRC_DIR, 'tests'))

CLIENT_IP = '127.0.0.1'

CLIENT_COUNT = 5

CLIENT_CAPACITY = 1024 * 1024 * 1024


class TagFS(unittest.TestCase):
    """
    Pruebas por unidades de TagFS.   
    """

    def setUp(self):
        """
        Inicializa el ambiente para realizar las pruebas.
        """
        self._clients = []
        clients_lock = threading.Lock()
        self._client_threads = []
        self._client_data_dirs = []
        client_data_dir_template = os.path.join(TESTS_DIR, 'client{number}')
        for index in xrange(CLIENT_COUNT):
            # Creating the client.
            client_data_dir = client_data_dir_template.format(number=index+1)
            self._client_data_dirs.append(client_data_dir)
            if os.path.isdir(client_data_dir):
                shutil.rmtree(client_data_dir)
            os.mkdir(client_data_dir)
            def create_client():
                client = TagFSClient(CLIENT_IP, client_data_dir, CLIENT_CAPACITY)
                with clients_lock:
                    self._clients.append(client)
            client_thread = threading.Thread(target=create_client)
            self._client_threads.append(client_thread)
            # Wait for the clients to start.
            clients_before = len(self._clients)
            clients_after = clients_before
            client_thread.start()
            while clients_before == clients_after:
                time.sleep(0.1)
                with clients_lock:
                    clients_after = len(self._clients)
            
    def tearDown(self):
        """
        Termina el ambiente creado para realizar las pruebas. 
        """
        for client in self._clients:
            client.terminate()
        for client_thread in self._client_threads:
            client_thread.join()
        for client_data_dir in self._client_data_dirs:
            shutil.rmtree(client_data_dir)

    def test_a(self):
        pass
    
    def test_b(self):
        pass
    

if __name__ == "__main__":
    module = os.path.basename(__file__)[:-3]
    suite = unittest.TestLoader().loadTestsFromName(module)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())

