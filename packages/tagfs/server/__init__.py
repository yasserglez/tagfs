# -*- coding: utf-8 -*-

"""
Implementación del servidor de TagFS.
"""

import socket

import Zeroconf
import Pyro.core

from tagfs.common import ZEROCONF_SERVICE_TYPE
from tagfs.server.remote import RemoteTagFSServer


class TagFSServer(object):
    """
    Servidor de TagFS.
    """
    
    def __init__(self, address, data_dir, capacity):
        """
        Inicializa una instancia de un servidor de TagFS.
        
        @type address: C{str}
        @param address: Dirección IP de la interfaz donde debe escuchar esta
           instancia del servidor de TagFS.
           
        @type data_dir: C{str}
        @param data_dir: Ruta absoluta al directorio utilizado para almacenar
            los archivos y otros datos relacionados con el funcionamiento
            del servidor.
            
        @type capacity: C{int}
        @param capacity: Capacidad de almacenamiento en bytes de este servidor.
            TagFS garantizará que la capacidad utilizada por todos los
            archivos almacenados en este servidor no sobrepasará esta
            capacidad.
        """
        self._continue = True
        self._sleep_time = 1
        self._address = address
        self.init_pyro(address, data_dir, capacity)        
        self.init_autodiscovery()

    def init_pyro(self, address, data_dir, capacity):
        """
        Inicializa el método utilizado para exportar las funcionalidades del 
        servidor TagFS a los clientes de la red.
        
        @type address: C{str}
        @param address: Dirección IP de la interfaz donde debe escuchar esta
           instancia del servidor de TagFS.
           
        @type data_dir: C{str}
        @param data_dir: Ruta absoluta al directorio utilizado para almacenar
            los archivos y otros datos relacionados con el funcionamiento
            del servidor.
            
        @type capacity: C{int}
        @param capacity: Capacidad de almacenamiento en bytes de este servidor.
            TagFS garantizará que la capacidad utilizada por todos los
            archivos almacenados en este servidor no sobrepasará esta
            capacidad.        
        """
        Pyro.core.initServer()
        self._pyro_remote = Pyro.core.ObjBase()
        self._daemon = Pyro.core.Daemon(host=self._address)
        self._pyro_uri = self._daemon.connect(self._pyro_remote, 'tagfs')
        self._remote = RemoteTagFSServer(address, data_dir, capacity, self._pyro_uri)
        self._pyro_remote.delegateTo(self._remote)

    def init_autodiscovery(self):
        """
        Inicializa el descubrimiento automático de los servidores TagFS.
        """
        self._zeroconf = Zeroconf.Zeroconf(self._daemon.hostname)
        zeroconf_service_name = '{n}.{t}'.format(n=self._pyro_uri, t=ZEROCONF_SERVICE_TYPE)
        self._zeroconf_service = Zeroconf.ServiceInfo(ZEROCONF_SERVICE_TYPE, zeroconf_service_name, 
                                                      socket.inet_aton(self._daemon.hostname),
                                                      self._daemon.port, 0, 0, {})
        self._zeroconf.registerService(self._zeroconf_service)
        
    def start(self):
        """
        Inicia el ciclo principal del servidor TagFS.
        """
        while self._continue:
            try:
                self._daemon.handleRequests(timeout=self._sleep_time)
            except KeyboardInterrupt:
                # End the main loop with CTRL-C.
                self._continue = False
        # Main loop of the daemon exited. Prepare to exit the program.
        self._remote.terminate()
        self._daemon.shutdown()
        self._zeroconf.unregisterService(self._zeroconf_service)
        self._zeroconf.close()
        
    def stop(self):
        """
        Detiene el ciclo principal del servidor TagFS.
        """
        self._continue = False
