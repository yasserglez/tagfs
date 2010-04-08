# -*- coding: utf-8 -*-

"""
Implementación de la clase base de los clientes TagFS.
"""

import random
import hashlib
import threading

import Zeroconf
import Pyro.core

from tagfs.common import ZEROCONF_SERVICE_TYPE


class TagFSClient(object):
    """
    Clase base de los clientes de TagFS.
    """
    
    def __init__(self, address):
        """
        Inicializa una instancia de un cliente TagFS.
        
        Solamente debe existir una instancia de esta clase en cada proceso
        ejecutando un cliente TagFS, debido a restricciones relacionadas con 
        las bibliotecas utilizadas para implementar el descubrimiento 
        automático de los servidores TagFS disponibles en la red.
        
        @type address: C{str}
        @param address: Dirección IP de la interfaz de red que se debe utilizar
           para comunicarse con los servidores TagFS.
        """
        self._address = address
        self.init_autodiscovery()
        
    def init_autodiscovery(self):
        """
        Inicializa el descubrimiento automático de los servidores.
        """
        self._servers = {}
        self._servers_mutex = threading.Lock()                
        self.addService = self.server_added
        self.removeService = self.server_removed
        self._zeroconf = Zeroconf.Zeroconf(self._address)
        self._zeroconf_browser = Zeroconf.ServiceBrowser(self._zeroconf, ZEROCONF_SERVICE_TYPE, self)
        
    def terminate(self):
        """
        Termina la ejecución del client TagFS. Despues de ejecutado este método 
        no se debe hacer ningún llamado a los métodos de esta instancia.
        """
        self._zeroconf.close()
        
    def server_added(self, zeroconf, service_type, service_name):
        """
        Método ejecutado cuando se descubre un nuevo servidor TagFS.
        
        @type zeroconf: C{Zeroconf}
        @param zeroconf: Instancia del servidor implementando la comunicación
            mediante Zeroconf Multicast DNS Service Discovery.
        
        @type service_type: C{str}
        @param service_type: Nombre completamente calificado del tipo
            de servicio que fue descubierto.
        
        @type service_name: C{str}
        @param service_name: Nombre completamente calificado del nombre 
            del servicio que fue descubierto.
        """
        with self._servers_mutex:
            pyro_uri = service_name[:-(len(service_type) + 1)]
            pyro_proxy = Pyro.core.getProxyForURI(pyro_uri)
            self._servers[pyro_uri] = pyro_proxy
        
    def server_removed(self, zeroconf, service_type, service_name):
        """
        Método ejecutado cuando un servidor TagFS deja de estar disponible.
        
        @type zeroconf: C{Zeroconf}
        @param zeroconf: Instancia del servidor implementando la comunicación
            mediante Zeroconf Multicast DNS Service Discovery.
            
        @type service_type: C{str}
        @param service_type: Nombre completamente calificado del tipo
            de servicio que fue descubierto.
        
        @type service_name: C{str}
        @param service_name: Nombre completamente calificado del nombre 
            del servicio que fue descubierto.                    
        """
        with self._servers_mutex:
            pyro_uri = service_name[:-(len(service_type) + 1)]
            del self._servers[pyro_uri]

    def put(self, name, description, tags, data, replication):
        """
        Añade un nuevo archivo al sistema de ficheros distribuido.
        
        @type name: C{str}
        @param name: Nombre del archivo que se quiere añadir al sistema de 
            ficheros distribuido. Es nombre se utilizará para crear el archivo 
            en un sistema de ficheros local cuando se obtenga del sistema de 
            ficheros distribuido. Será posible realizar búsquedas en el sistema 
            distribuido introduciendo términos incluídos en el nombre.
        
        @type description: C{str}
        @param description: Descripción del archivo que se quiere añadir al 
            sistema de ficheros distribuido. Será posible realizar búsquedas 
            en el sistema distribuido introduciendo términos incluídos en la 
            descripción.
        
        @type tags: C{set}
        @param tags: Conjunto de tags que se deben asociar a este archivo. Cada 
            tag debe ser una palabra y no debe contener espacios. Será posible 
            relizar búsquedas en el sistema distribuido introduciendo tags.

        @type data: C{str}
        @param data: Contenido del archivo.
        
        @type replication: C{int}
        @param replication: Porciento de replicación que se debe utillizar para 
            este archivo. El cliente intentará que este archivo se almacene 
            en un número de nodos correspondiente al porciento indicado del 
            total de nodos disponibles en el momento en que se añade el archivo.
        """
        with self._servers_mutex:
            size = len(data)
            
            # Servers where the file should be saved.
            num_servers = max(1, int((replication * len(self._servers)) / 100.0))
            servers = [server for server in self._servers.values()
                       if (server.status()['empty_space'] >= size)]
            servers = random.sample(servers, min(len(servers), num_servers))
            
            # Collect the metadata of the file.
            md5_hash = hashlib.new('md5')
            md5_hash.update(data)
            info = {}
            info['hash'] = md5_hash.hexdigest()
            info['tags'] = tags
            info['description'] = description
            info['name'] = name
            info['size'] = str(size)
            
            # Save the file in each selected server.
            for server in servers:
                server.put(data, info)
