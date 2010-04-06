# -*- coding: utf-8 -*-

"""
Implementación del servidor de TagFS.
"""

import time
import socket

from tagfs.common import ZEROCONF_SERVICE_TYPE
from tagfs.server.remote import RemoteTagFSServer
from tagfs.contrib.Zeroconf import Zeroconf, ServiceInfo
from tagfs.contrib.Pyro import core


class TagFSServer(object):
    """
    Servidor de TagFS.
    """
    
    def __init__(self, address):
        """
        Inicializa una instancia de un servidor de TagFS.
        
        Solamente debe existir una instancia de esta clase en cada proceso
        ejecutando un servidor TagFS, debido a restricciones relacionadas con las 
        bibliotecas utilizadas para implementar el descubrimiento automático de 
        los servidores TagFS disponibles en la red.
        
        @type address: C{str}
        @param address: Dirección IP de la interfaz donde debe escuchar esta
           instancia del servidor de TagFS.
        """
        self.init_pyro(address)
        self.init_autodiscovery()
        
    def init_pyro(self, address):
        """
        Inicializa el método utilizado para exportar las funcionalidades del 
        servidor TagFS a los clientes de la red.
        
        @type address: C{str}
        @param address: Dirección IP de la interfaz donde debe escuchar esta
           instancia del servidor de TagFS.
        """
        core.initServer()
        self._daemon = core.Daemon(host=address)
        self._pyro_uri = self._daemon.connect(RemoteTagFSServer(), 'tagfs')
        
    def init_autodiscovery(self):
        """
        Inicializa el descubrimiento automático de los servidores TagFS.
        """
        self._zeroconf = Zeroconf(self._daemon.hostname)
        zeroconf_service_name = '{n}.{t}'.format(n=self._pyro_uri, t=ZEROCONF_SERVICE_TYPE)
        self._zeroconf_service = ServiceInfo(ZEROCONF_SERVICE_TYPE, zeroconf_service_name, 
                                             socket.inet_aton(self._daemon.hostname),
                                             self._daemon.port, 0, 0, {})
        self._zeroconf.registerService(self._zeroconf_service)
        
    def start(self):
        """
        Inicia el ciclo principal del servidor TagFS.
        """
        while True:
            try:
                self._daemon.handleRequests()
                time.sleep(1)
            except KeyboardInterrupt:
                # End the main loop with CTRL-C.
                break
        # Main loop of the daemon exited. Prepare to exit the program.
        self._zeroconf.unregisterService(self._zeroconf_service)
        self._zeroconf.close()
