# -*- coding: utf-8 -*-

"""
Implementación del servidor TagFS compartido en la red.   
"""

import os
import time
import hashlib
import threading

import sync
import magic
import whoosh.index
import whoosh.fields
import whoosh.query
import whoosh.qparser
import Pyro.core
import Zeroconf

from tagfs.common import ZEROCONF_SERVICE_TYPE
from tagfs.common.timeprovider import LocalTimeProvider


class RemoteTagFSServer(object):
    """
    Servidor TagFS compartido en la red utilizando Pyro. 
    """

    def __init__(self,  address, data_dir, capacity, ntp_server = None):
        """
        Inicializa una instancia de un servidor TagFS compartido en la red.
        
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
        self._address = address
        self._data_dir = data_dir
        if not os.path.isdir(self._data_dir):
            os.mkdir(self._data_dir)
        self._init_index()
        self._init_files()
        self._init_status(capacity)
        self._init_autodiscovery()
        self._mrsw_lock = sync.mrsw()
        # Keep this last! This requires the index, locks, etc.
        self._sync_thread = threading.Thread(target=self._sync_servers)
        self._sync_thread.start()
        # TODO Change to use ntp or local.
        if ntp_server:
            pass
        else:
            self._time_provider = LocalTimeProvider()
        
    def _init_index(self):
        """
        Inicializa el índice, implementado utilizando Whoosh, que contiene
        la información acerca de los archivos almacenados en este servidor
        de TagFS.
        """
        self._encoding = 'utf-8'
        self._index_schema = whoosh.fields.Schema(
            hash=whoosh.fields.ID(stored=True, unique=True),
            tags=whoosh.fields.KEYWORD(stored=True, lowercase=True, 
                                       scorable=True, field_boost=2.0),
            description=whoosh.fields.TEXT(stored=True),
            name=whoosh.fields.TEXT(stored=True),
            owner=whoosh.fields.STORED(),
            group=whoosh.fields.STORED(),
            perms=whoosh.fields.STORED(),
            size=whoosh.fields.STORED(),
            path=whoosh.fields.STORED(),
            type=whoosh.fields.STORED(),
            time=whoosh.fields.STORED(),
            action=whoosh.fields.STORED(),
        )
        index_dir = os.path.join(self._data_dir, 'index')
        if not os.path.isdir(index_dir):
            os.mkdir(index_dir)
            self._index = whoosh.index.create_in(index_dir, self._index_schema)
        else:
            self._index = whoosh.index.open_dir(index_dir)
        
    def _init_files(self):
        """
        Inicializa el directorio que contiene los archivos almacenados 
        en este servidor de TagFS. time.mktime(time.gmtime())Los archivos no se almacenarán directamente
        en la raíz de este directorio sino en un serie de directorios anidados
        para evitar que este directorio tenga muchas entradas y se haga
        muy lento el acceso a un archivo.
        """
        self._files_dir = os.path.join(self._data_dir, 'files')
        if not os.path.isdir(self._files_dir):
            os.mkdir(self._files_dir)
            
    def _init_status(self, capacity):
        """
        Inicializa el diccionario de estado de este servidor de TagFS. Este 
        diccionario es el que se les envía a los clientes como respuesta
        del método C{status()}.
        
        Actualmente este diccionario contiene información acerca de la 
        capacidad de almacenamiento de este servidor TagFS y la cantidad
        de espacio libre.
        
        @type capacity: C{int}
        @param capacity: Capacidad de almacenamiento en bytes de este servidor.
            TagFS garantizará que la capacidad utilizada por todos los
            archivos almacenados en este servidor no sobrepasará esta
            capacidad.        
        """
        self._status = {}
        self._status['capacity'] = long(capacity)
        # Calculate the space used in the data directory.
        data_dir_size = 0L
        get_file_size_root = lambda root, file: os.path.getsize(os.path.join(root, file))
        for root, _, files in os.walk(self._data_dir):
            get_file_size = lambda file: get_file_size_root(root, file)
            data_dir_size += sum(map(get_file_size, files))
        self._status['empty_space'] = capacity - data_dir_size
        
    def _init_autodiscovery(self):
        """
        Inicializa el descubrimiento automático de los servidores.
        """
        self._servers = {}
        self._servers_mutex = threading.Lock()                
        self.addService = self._server_added
        self.removeService = self._server_removed
        self._zeroconf = Zeroconf.Zeroconf(self._address)
        self._zeroconf_browser = Zeroconf.ServiceBrowser(self._zeroconf, ZEROCONF_SERVICE_TYPE, self)
        
    def _server_added(self, zeroconf, service_type, service_name):
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
        
    def _server_removed(self, zeroconf, service_type, service_name):
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
            
    def _sync_servers(self):
        """
        Método que garantiza la sincronización de los servidores.
        """
        sync_sleep = 5 * 60 # seconds
        self._sync_cond = threading.Condition()
        self._sync_continue = True
        while self._sync_continue:
            with self._servers_mutex:
                self._mrsw_lock.write_in()
                try:
                    # TODO: Synchronize the servers here!
                    pass
                finally:
                    self._mrsw_lock.write_out()
            self._sync_cond.acquire()
            self._sync_cond.wait(sync_sleep)
            self._sync_cond.release()
        
    def status(self):
        """
        Brinda información a los clientes TagFS acerca del estado de este
        servidor. Por ejemplo: cantidad de espacio disponible para almacenar
        nuevos archivos.
        
        @rtype: C{dict}
        @return: Diccionario que contiene información acerca del estado 
            del servidor.
        """
        self._mrsw_lock.read_in()
        try:
            return self._status
        finally:
            self._mrsw_lock.read_out()
        
    def get(self, file_hash):
        """
        Obtiene el contenido del archivo identificado por C{file_hash}
        
        @type file_hash: C{str}
        @param file_hash: Identificador del archivo cuyos datos se quiere 
            obtener. Este hash identifica al archivo únicamente dentro del 
            sistema de ficheros distribuidos, a partir de sus etiquetas y 
            su nombre.
            
        @rtype: C{str}
        @return: Contenido del archivo identificado por C{file_hash} si
            este archivo existe, C{None} si no hay almacenado en este
            servidor un archivo identificado por el hash dado.
        """
        self._mrsw_lock.read_in()
        try:
            searcher = self._index.searcher()
            doc = searcher.document(hash=file_hash.decode(self._encoding))
            if doc is not None:
                file_path = os.path.join(self._files_dir, doc['path'])
                with open(file_path, 'rb') as file:
                    return file.read()
            else:
                return None
        finally:
            self._mrsw_lock.read_out()
        
    def put(self, file_data, file_info):
        """
        Almacena un nuevo archivo en este servidor del sistema de 
        archivos distribuidos.
        
        @type file_data: C{str}
        @param file_data: Contenido del archivo que se quiere almacenar.
        
        @type file_info: C{dict}
        @param file_info: Diccionario con los metadatos del archivo.         
        """
        self._mrsw_lock.write_in()
        try:
            # Save the file in the files directory.
            file_name = file_info['name']
            file_hash = hashlib.md5(u' ' .join([tag.decode(self._encoding) 
                                              for tag in file_info['tags']]) 
                                    + file_name.decode(self._encoding)).hexdigest()
            file_path = os.path.join(self._files_dir, os.path.sep.join(file_hash[0:5]), file_name)
            if not os.path.isdir(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            with open(file_path, 'w') as file:
                file.write(file_data)
    
            # Add the metadata of the file to the index.
            file_path = file_path[len(self._files_dir) + 1:]
            writer = self._index.writer()
            writer.delete_by_term('hash', file_hash.decode(self._encoding))
            writer.add_document(
                hash=file_hash.decode(self._encoding),
                tags=u' '.join([tag.decode(self._encoding) for tag in file_info['tags']]),
                description=file_info['description'].decode(self._encoding),
                name=file_info['name'].decode(self._encoding),
                size=file_info['size'].decode(self._encoding),
                owner=file_info['owner'].decode(self._encoding),
                group=file_info['group'].decode(self._encoding),
                perms=file_info['perms'].decode(self._encoding),
                path=file_path.decode(self._encoding),
                type=magic.whatis(file_data),
                time=str(self._time_provider.get_time()).decode(self._encoding),
                action=u'add'                
            )               
            writer.commit()
    
            # Update the empty space of this server.
            self._status['empty_space'] -= long(file_info['size'])
        finally:
            self._mrsw_lock.write_out()
        
    def remove(self, file_hash):
        """
        Elimina un archivo almacenado en este servidor. Si este servidor
        no tiene almacenado un archivo identificado con el hash dado
        no se realizará ninguna acción.
        
        @type file_hash: C{str}
        @param file_hash: Identificador del archivo que se quiere eliminar. 
            Este hash identifica al archivo únicamente dentro del sistema de 
            ficheros distribuido a partir de sus etiquetas y su nombre.
        """
        self._mrsw_lock.write_in()
        try:
            searcher = self._index.searcher()
            doc = searcher.document(hash=file_hash.decode(self._encoding))
            if doc is not None:                
                # Remove the file from the files directory.
                os.remove(os.path.join(self._files_dir, doc['path']))
                
                # Remove the metadata of the file from the index.
                writer = self._index.writer()
                writer.delete_by_term('hash', file_hash.decode(self._encoding))
                writer.add_document(
                    hash=file_hash.decode(self._encoding),
                    time=self._time_provider.get_time(),
                    action=u'delete'                
                )
                writer.commit()

                # Update the empty space in this server.
                self._status['empty_space'] += long(doc['size'])
        finally:
            self._mrsw_lock.write_out()
        
    def list(self, tags):
        """
        Lista los archivos almacenados en este servidor que tienen todos
        los tags especificados en el conjunto C{tags}.
        
        @type tags: C{set}
        @param tags: Conjunto de tags que deben tener los archivos.
        
        @rtype: C{set}
        @return: Conjunto con los hash de los archivos que tienen los tags 
            especificados mediante el conjunto C{tags}.
        """
        self._mrsw_lock.read_in()
        try:
            searcher = self._index.searcher()
            tags_terms = [tag.decode(self._encoding).lower() for tag in tags]
            query = whoosh.query.And([whoosh.query.Term('tags', term) for term in tags_terms])
            return set([result['hash'] for result in searcher.search(query)])
        finally:
            self._mrsw_lock.read_out()

    def search(self, text):
        """
        Realiza una búsqueda de texto libre en los tags, la descripción y el 
        nombre de los archivos almacenados en este servidor.
        
        @type text: C{str}
        @param text: Texto de la búsqueda que se quiere realizar.
        
        @rtype: C{set}
        @return: Conjunto con los hash de los archivos que son relevantes 
            para la búsqueda de texto libre C{text}.
        """
        self._mrsw_lock.read_in()
        try:
            searcher = self._index.searcher()
            default_fields = ['tags', 'description', 'name']
            parser = whoosh.qparser.MultifieldParser(default_fields, schema=self._index_schema)
            query = parser.parse(text.decode(self._encoding))
            return set([result['hash'] for result in searcher.search(query)])
        finally:
            self._mrsw_lock.read_out()
                                   
    def info(self, file_hash):
        """
        Obtiene información a partir del hash de un archivo.
        
        @type file_hash: C{str}
        @param file_hash: Identificador del archivo cuya información se quiere 
            obtener. Este hash identifica al archivo únicamente dentro del 
            sistema de ficheros distribuidos a partir de sus etiquetas y su 
            nombre.
            
        @rtype: C{dict}
        @return: Diccionario con los metadatos del archivo si este servidor
            tiene almacenado un archivo identificado por el hash dado,
            C{None} en caso contrario.
        """
        self._mrsw_lock.read_in()
        try:
            searcher = self._index.searcher()
            doc = searcher.document(hash=file_hash.decode(self._encoding))
            if doc is not None:
                info = {}
                info['hash'] = doc['hash']
                info['tags'] = set(doc['tags'].split())
                info['description'] = doc['description']
                info['name'] = doc['name']
                info['size'] = doc['size']
                info['type'] = doc['type']
                info['owner'] = doc['owner']
                info['group'] = doc['group']
                info['perms'] = doc['perms']
                info['time']=time.gmtime(float(doc['time']))
                return info
            else:
                return None
        finally:
            self._mrsw_lock.read_out()        
            
    def get_all_tags(self):
        """
        Obtiene un conjunto con todas los tags que tiene algún archivo 
        almacenado en este servidor.
        
        @rtype: C{set}
        @return: Conjunto con las etiquetas en este servidor.
        """
        reader = self._index.reader()
        searcher = self._index.searcher()
        tags = set()
        for tag in reader.lexicon('tags'):
            # Ugly hack! Returns tags that were removed from the index?!
            query = whoosh.query.Term('tags', tag)
            results = searcher.search(query, limit=1)
            if len(results) > 0:
                tags.add(tag)
        return tags
    
    def get_popular_tags(self, number):
        """
        Obtiene un conjunto con los tags más populares de los archivos 
        almacenados en este servidor.
        
        @type number: C{int}
        @param number: Cantidad de tags populares deseadas.
        
        @rtype: C{set}
        @return: Conjunto de tuplas de la forma (frecuencia, tag) 
        """        
        reader = self._index.reader()
        return set(reader.most_distinctive_terms('tags', number, u''))
        
    def terminate(self):
        """
        Este método es utilizado por la instancia de la clase C{TagFSServer} para
        indicar que va a dejar de estar disponible en la red este servidor y que
        se deben guardar todos los recursos abiertos.
        """
        self._sync_continue = False
        self._sync_cond.acquire()
        self._sync_cond.notify()
        self._sync_cond.release()
        self._sync_thread.join()
        self._index.close()
