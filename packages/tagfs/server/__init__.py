# -*- coding: utf-8 -*-

"""
Implementación del servidor de TagFS.
"""

import socket
import time
import uuid

from tagfs.common import ZEROCONF_SERVICE_TYPE
from tagfs.contrib.Zeroconf import Zeroconf, ServiceInfo


class TagFSServer(object):
    """
    Servidor de TagFS.
    """
    
    def __init__(self, address, port):
        """
        Inicializa una instancia de un servidor de TagFS.
        
        Solamente debe existir una instancia de esta clase en cada proceso
        ejecutando un servidor TagFS, debido a restricciones relacionadas con las 
        bibliotecas utilizadas para implementar el descubrimiento automático de 
        los servidores TagFS disponibles en la red.
        
        @type address: C{str}
        @param address: Dirección IP de la interfaz donde debe escuchar esta
           instancia de un servidor de TagFS.
        
        @type port: C{int}
        @param port: Puerto donde debe escuchar esta instancia de un servidor TagFS.
        """
        self._address = address
        self._port = port
        self.init_autodiscovery()
        
    def init_autodiscovery(self):
        """
        Inicializa el descubrimiento automático de los servidores TagFS.
        """
        self._zeroconf = Zeroconf(self._address)
        zeroconf_service_name = '{n}.{t}'.format(n=uuid.uuid1(), t=ZEROCONF_SERVICE_TYPE)
        self._zeroconf_service = ServiceInfo(ZEROCONF_SERVICE_TYPE, zeroconf_service_name, 
                                             socket.inet_aton(self._address),
                                             self._port, 0, 0, {})
        self._zeroconf.registerService(self._zeroconf_service)
        
    def start(self):
        """
        Inicia el ciclo principal del servidor TagFS.
        """
        try:
            time.sleep(30)
        except KeyboardInterrupt:
            # Ignore CTRL-C so it can be used to stop the server in this first version.
            pass
        finally:
            self._zeroconf.unregisterService(self._zeroconf_service)
            self._zeroconf.close()
