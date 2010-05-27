# -*- coding: utf-8 -*-

"""
Implementación de los clientes TagFS.
"""

import random
import threading

import Zeroconf
import Pyro.core

from tagfs.common import ZEROCONF_SERVICE_TYPE
from tagfs.server import TagFSServer


class TagFSClient(object):
    """
    Clase base de los clientes de TagFS.
    """
    
    def __init__(self, address, data_dir, capacity):
        """
        Inicializa una instancia de un cliente TagFS.
        
        @type address: C{str}
        @param address: Dirección IP de la interfaz de red que se debe utilizar
           para comunicarse con los servidores TagFS y en la que debe escuchar
           el servidor que se ejecutará en este cliente.
           
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
        self._address = address
        self._data_dir = data_dir
        self._capacity = capacity
        self.init_server()
        self.init_autodiscovery()
        
    def init_server(self):
        """
        Inicializa el servidor ejecutado por este cliente.
        """
        self._server = TagFSServer(self._address, self._data_dir, self._capacity)
        self._server_thread = threading.Thread(target=self._server.start)
        self._server_thread.start()
        
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
        Termina la ejecución del client TagFS. Después de ejecutado este método 
        no se debe hacer ningún llamado a los métodos de esta instancia.
        """
        self._server.stop()
        self._server_thread.join()
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

    def put(self, name, description, tags, owner, group, perms, data, replication):
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
            
        @type owner: C{str}
        @param owner: Usuario que va a ser el dueño del fichero.
        
        @type group: C{str}
        @param group: Grupo del fichero.
        
        @type perms: C{int}
        @param perms: Permisos del fichero.

        @type data: C{str}
        @param data: Contenido del archivo.
        
        @type replication: C{int}
        @param replication: Porciento de replicación que se debe utillizar para 
            este archivo. El cliente intentará que este archivo se almacene 
            en un número de nodos correspondiente al porciento indicado del 
            total de nodos disponibles en el momento en que se añade el archivo.
            
        @rtype: C{bool}
        @return: Este método retornará C{True} si el archivo se logró almacenar
            en al menos un servidor del sistema distribuido o C{False} en caso
            contrario. Es posible que aunque existan servidores conectados
            no se pueda almacenar el archivo porque estos no tengan la 
            capacidad de almacenamiento necesaria. 
        """
        with self._servers_mutex:
            size = len(data)
            
            # Servers where the file should be saved.
            num_servers = max(1, int((replication * len(self._servers)) / 100.0))
            servers = [server for server in self._servers.values()
                       if (server.status()['empty_space'] >= size)]
            servers = random.sample(servers, min(len(servers), num_servers))
            
            # Collect the metadata of the file.
            info = {}
            info['tags'] = tags
            info['description'] = description
            info['name'] = name
            info['size'] = str(size)
            info['owner'] = owner
            info['group'] = group
            info['perms'] = str(perms)
            
            # Save the file in each selected server.
            saved = False
            for server in servers:
                try:
                    server.put(data, info)
                except Exception:
                    # Ignoring any exception here. If the server is not accesible 
                    # it will be eventually removed from the server list when is 
                    # detected by Zeroconf.
                    pass
                else:
                    saved = True
        return saved
    
    def get(self, file_hash):
        """
        Obtiene el contenido del archivo identificado por C{file_hash}
        
        @type file_hash: C{str}
        @param file_hash: Hash del contenido del archivo cuyos datos
            se quiere obtener. Este hash identifica al archivo únicamente
            dentro del sistema de ficheros distribuidos.
            
        @rtype: C{str}
        @return: Contenido del archivo identificado por C{file_hash} si
            este archivo existe, C{None} si no hay almacenado en el 
            sistema de ficheros distribuido un archivo identificado 
            por el hash dado.
        """
        with self._servers_mutex:
            for server in self._servers.itervalues():
                try:
                    data = server.get(file_hash)
                    if data is not None:
                        return data
                except Exception:
                    # Ignoring any exception here.
                    pass
        return None
    
    def remove(self, file_hash):
        """
        Elimina un archivo almacenado en el sistema de ficheros distribuido.
        Si el sistema de ficheros no tiene almacenado un archivo identificado
        con el hash dado no se realizará ninguna acción.
        
        @type file_hash: C{str}
        @param file_hash: Hash del contenido del archivo que se quiere
            eliminar. Este hash identifica al archivo únicamente
            dentro del sistema de ficheros distribuido.
        """
        with self._servers_mutex:
            for server in self._servers.itervalues():
                try:
                    server.remove(file_hash)
                except Exception:
                    # Ignoring any exception here.
                    pass

    def list(self, tags):
        """
        Lista los archivos almacenados en el sistema de ficheros distribuido
        que tienen todos los tags especificados en el conjunto C{tags}.
        
        @type tags: C{set}
        @param tags: Conjunto de tags que deben tener los archivos.
        
        @rtype: C{set}
        @return: Conjunto con los hash de los archivos que tienen los tags 
            especificados mediante el conjunto C{tags}.
        """
        all_results = set()
        with self._servers_mutex:
            for server in self._servers.itervalues():
                try:
                    server_results = server.list(tags)
                    all_results |= server_results
                except Exception:
                    # Ignoring any exception here.
                    pass                    
        return all_results
    
    def search(self, text):
        """
        Realiza una búsqueda de texto libre en los tags, la descripción y el 
        nombre de los archivos almacenados en el sistema de ficheros
        distribuido.
        
        @type text: C{str}
        @param text: Texto de la búsqueda que se quiere realizar.
        
        @rtype: C{set}
        @return: Conjunto con los hash de los archivos que son relevantes 
            para la búsqueda de texto libre C{text}.
        """
        all_results = set()
        with self._servers_mutex:
            for server in self._servers.itervalues():
                try:
                    server_results = server.search(text)
                    all_results |= server_results
                except Exception:
                    # Ignoring any exception here.
                    pass                    
        return all_results

    def info(self, file_hash):
        """
        Obtiene información a partir del hash de un archivo.
        
        @type file_hash: C{str}
        @param file_hash: Hash del contenido del archivo cuya información
            se quiere obtener. Este hash identifica al archivo únicamente
            dentro del sistema de ficheros distribuidos.
            
        @rtype: C{dict}
        @return: Diccionario con los metadatos del archivo si el sistema
            de ficheros distribuido tiene almacenado un archivo identificado 
            por el hash dado, C{None} en caso contrario.
        """
        with self._servers_mutex:
            for server in self._servers.itervalues():
                try:
                    info = server.info(file_hash)
                    if info is not None:
                        return info
                except Exception:
                    # Ignoring any exception here.
                    pass
        return None
    
    def get_all_tags(self):
        """
        Permite obtener un conjunto con todas los tags en el sistema.
        
        @rtype: C{set}
        @return: Conjunto con los nombres de las etiquetas del sistema.
        """
        all_results = set()
        with self._servers_mutex:
            for server in self._servers.itervalues():
                try:
                    server_results = server.get_all_tags()
                    all_results |= server_results
                except Exception:
                    # Ignoring any exception here.
                    pass
        return all_results

    def get_popular_tags(self, number):
        """
        Permite obtener un conjunto con los tags más populares del sistema.
        
        @type number: C{int}
        @param number: Cantidad de tags populares deseadas.
        
        @rtype: C{set}
        @return: Conjunto con los nombres de las etiquetas del sistema.
        """
        all_results = {}
        with self._servers_mutex:
            for server in self._servers.itervalues():
                try:
                    server_results = server.get_popular_tags(number)
                    for frequency, tag in server_results:
                        if tag in all_results:
                            all_results[tag].append(frequency)
                        else:
                            all_results[tag] = [frequency]
                except Exception:
                    # Ignoring any exception here.
                    pass
        result = []
        for tag, freqs in all_results.iteritems():
            mean = (sum(freqs) / len(freqs), tag)
            result.append(mean)
        result.sort()
        return set([tag for (_, tag) in result[:number]])
