# -*- coding: utf-8 -*-

"""
Pruebas por unidad del Sistema.   
"""

import os
import sys
import time
import random
import hashlib
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

FILES_DIR = os.path.join(TESTS_DIR, 'files')

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

    def testPut(self):
        client = random.choice(self._clients)
        client.put('UbuntuLogo.png',  'The Ubuntu logo.', 
                   set(['ubuntu', 'gnu', 'linux', 'logo']), 'tagfs', 'tagfs', 644, 
                   open(os.path.join(FILES_DIR, 'UbuntuLogo.png')).read(), 100)        
        client.put('UbuntuIsHumanity.ogv',  'Ubuntu is Humanity video.', 
                   set(['ubuntu', 'gnu', 'linux', 'humanity', 'video']), 'tagfs', 'tagfs', 
                   644, open(os.path.join(FILES_DIR, 'UbuntuIsHumanity.ogv')).read(), 50)
        results = client.list(set(['ubuntu']))
        self.assertEquals(len(results), 2)
        
    def testGet(self):
        original_data = open(os.path.join(FILES_DIR, 'UbuntuLogo.png')).read()
        client = random.choice(self._clients)
        client.put('UbuntuLogo.png',  'The Ubuntu logo.', 
                   set(['ubuntu', 'gnu', 'linux', 'logo']), 
                   'tagfs', 'tagfs', 644, original_data, 100)
        results = client.list(set(['ubuntu']))
        hash = results.pop()
        tagfs_data = client.get(hash)
        self.assertEqual(hashlib.md5(original_data).digest(), 
                         hashlib.md5(tagfs_data).digest())
        
    def testRemove(self):
        client = random.choice(self._clients)
        client.put('UbuntuLogo.png',  'The Ubuntu logo.', 
                   set(['ubuntu', 'gnu', 'linux', 'logo']), 'tagfs', 'tagfs', 644, 
                   open(os.path.join(FILES_DIR, 'UbuntuLogo.png')).read(), 20)        
        results = client.list(set(['ubuntu']))
        self.assertEquals(len(results), 1)
        client.remove(results.pop())
        self.assertEquals(len(results), 0)
        
    def testList(self):
        client = random.choice(self._clients)
        client.put('UbuntuLogo.png',  'The Ubuntu logo.', 
                   set(['ubuntu', 'gnu', 'linux', 'logo']), 'tagfs', 'tagfs', 644, 
                   open(os.path.join(FILES_DIR, 'UbuntuLogo.png')).read(), 100)        
        client.put('UbuntuIsHumanity.ogv',  'Ubuntu is Humanity video.', 
                   set(['ubuntu', 'gnu', 'linux', 'humanity', 'video']), 'tagfs', 'tagfs', 
                   644, open(os.path.join(FILES_DIR, 'UbuntuIsHumanity.ogv')).read(), 50)
        self.assertEquals(len(client.list(set(['ubuntu', 'logo', 'video']))), 0)
        self.assertEquals(len(client.list(set(['logo']))), 1)
        self.assertEquals(len(client.list(set(['video']))), 1)
        self.assertEquals(len(client.list(set(['ubuntu']))), 2)
        
    def testSearch(self):
        client = random.choice(self._clients)
        client.put('UbuntuLogo.png',  'The Ubuntu logo.', 
                   set(['ubuntu', 'gnu', 'linux', 'logo']), 'tagfs', 'tagfs', 644, 
                   open(os.path.join(FILES_DIR, 'UbuntuLogo.png')).read(), 100)        
        client.put('UbuntuIsHumanity.ogv',  'Ubuntu is Humanity video.', 
                   set(['ubuntu', 'gnu', 'linux', 'humanity', 'video']), 'tagfs', 'tagfs', 
                   644, open(os.path.join(FILES_DIR, 'UbuntuIsHumanity.ogv')).read(), 50)
        results = client.search('ubuntu gnu linux logo')
        self.assertEquals(client.info(results.pop())['name'], 'UbuntuLogo.png')
        results = client.search('humanity')
        self.assertEquals(client.info(results.pop())['name'], 'UbuntuIsHumanity.ogv')        
    
    def testInfo(self):
        client = random.choice(self._clients)
        name = 'UbuntuLogo.png'
        desc = 'The Ubuntu logo.'
        tags = set(['ubuntu', 'gnu', 'linux', 'logo'])
        owner = 'tagfs'
        group = 'tagfs'
        perms = 644
        data = open(os.path.join(FILES_DIR, 'UbuntuLogo.png')).read()
        client.put(name,  desc, tags, owner, group, perms, data, 20)        
        hash = client.list(set(['ubuntu'])).pop()
        info = client.info(hash)
        self.assertEquals(info['tags'], tags)
        self.assertEquals(info['description'], desc)
        self.assertEquals(info['name'], name)
        self.assertEquals(int(info['size']), len(data))
        self.assertEquals(info['owner'], owner)
        self.assertEquals(info['group'], group)
        self.assertEquals(int(info['perms']), perms)
    
    def testGetAllTags(self):
        client = random.choice(self._clients)
        logo_tags = set(['ubuntu', 'gnu', 'linux', 'logo'])
        client.put('UbuntuLogo.png',  'The Ubuntu logo.', 
                   logo_tags, 'tagfs', 'tagfs', 644, 
                   open(os.path.join(FILES_DIR, 'UbuntuLogo.png')).read(), 100)
        video_tags = set(['ubuntu', 'gnu', 'linux', 'humanity', 'video'])        
        client.put('UbuntuIsHumanity.ogv',  'Ubuntu is Humanity video.', 
                   video_tags, 'tagfs', 'tagfs', 
                   644, open(os.path.join(FILES_DIR, 'UbuntuIsHumanity.ogv')).read(), 50)
        all_tags = client.get_all_tags()
        self.assertEquals(all_tags, logo_tags | video_tags)
        
    def testGetPopularTags(self):
        client = random.choice(self._clients)
        client.put('UbuntuLogo.png',  'The Ubuntu logo.', 
                   set(['ubuntu', 'gnu', 'linux', 'logo']), 'tagfs', 'tagfs', 644, 
                   open(os.path.join(FILES_DIR, 'UbuntuLogo.png')).read(), 100)        
        client.put('UbuntuIsHumanity.ogv',  'Ubuntu is Humanity video.', 
                   set(['ubuntu', 'gnu', 'linux', 'humanity', 'video']), 'tagfs', 'tagfs', 
                   644, open(os.path.join(FILES_DIR, 'UbuntuIsHumanity.ogv')).read(), 50)
        popular_tags = client.get_popular_tags(3)
        self.assertEquals(popular_tags, set(['ubuntu', 'logo', 'linux']))


if __name__ == "__main__":
    module = os.path.basename(__file__)[:-3]
    suite = unittest.TestLoader().loadTestsFromName(module)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())
