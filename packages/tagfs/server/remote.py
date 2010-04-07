# -*- coding: utf-8 -*-

"""
Implementación del servidor TagFS compartido en la red.   
"""

import os

import Pyro.core
import whoosh.index
import whoosh.fields
import whoosh.qparser


class RemoteTagFSServer(Pyro.core.SynchronizedObjBase):
    """
    Servidor TagFS compartido en la red utilizando Pyro. 
    """

    def __init__(self, data_dir, capacity):
        """
        Inicializa una instancia de un servidor TagFS compartido en la red.
        Como parte de la inicialización de este objeto se ejecuta el método 
        encargado de inicializar los aspectos relacionados con Pyro para 
        garantizar que los métodos de esta clase puedan ser ejecutados por 
        los clientes TagFS.
        
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
        super(RemoteTagFSServer, self).__init__()
        self._data_dir = data_dir
        if not os.path.isdir(self._data_dir):
            os.mkdir(self._data_dir)
        self._init_index()
        self._init_files()
        self._init_status(capacity)
        
    def _init_index(self):
        """
        Inicializa el índice, implementado utilizando Whoosh, que contiene
        la información acerca de los archivos almacenados en este servidor
        de TagFS.
        """
        self._schema = whoosh.fields.Schema(
            hash=whoosh.fields.ID(stored=True, unique=True),
            tags=whoosh.fields.KEYWORD(stored=True, lowercase=True, 
                                       scorable=True, field_boost=2.0),
            description=whoosh.fields.TEXT(stored=True),
            name=whoosh.fields.TEXT(stored=True),
            size=whoosh.fields.STORED(),
            path=whoosh.fields.STORED(),
        )
        index_dir = os.path.join(self._data_dir, 'index')
        if not os.path.isdir(index_dir):
            os.mkdir(index_dir)
            self._index = whoosh.index.create_in(index_dir, self._schema)
        else:
            self._index = whoosh.index.open_dir(index_dir)
        if self._index.doc_count() > 0:
            self._index.optimize()
        
    def _init_files(self):
        """
        Inicializa el directorio que contiene los archivos almacenados 
        en este servidor de TagFS. Los archivos no se almacenarán directamente
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
        for root, dirs, files in os.walk(self._data_dir):
            get_file_size = lambda file: get_file_size_root(root, file)
            data_dir_size += sum(map(get_file_size, files))
        self._status['empty_space'] = capacity - data_dir_size
        
    def _path_from_file_hash(self, file_hash):
        """
        Obtiene del índice la ruta relativa al directorio de datos correspondiente
        al archivo identificado con el hash dado y retorna la ruta absoluta
        a este archivo.
        
        @type file_hash: C{str}
        @param file_hash: Hash del contenido del archivo cuya ruta absoluta
            se quiere obtener. Este hash identifica al archivo únicamente
            dentro del sistema de ficheros distribuidos.
            
        @rtype: C{str}
        @return: Ruta absoluta del archivo identificado por el hash dado.
        """
        searcher = self._index.searcher()
        doc = searcher.document(hash=file_hash.decode('utf-8'))
        return os.path.join(self._files_dir, doc['path'])
        
    def status(self):
        """
        Brinda información a los clientes TagFS acerca del estado de este
        servidor. Por ejemplo: cantidad de espacio disponible para almacenar
        nuevos archivos.
        
        @rtype: C{dict}
        @return: Diccionario que contiene información acerca del estado 
            del servidor.
        """
        return self._status
        
    def get(self, file_hash):
        """
        Obtiene el contenido del archivo identificado por C{file_hash}
        
        @type file_hash: C{str}
        @param file_hash: Hash del contenido del archivo cuyos datos
            se quiere obtener. Este hash identifica al archivo únicamente
            dentro del sistema de ficheros distribuidos.
            
        @rtype: C{str}
        @return: Contenido del archivo identificado por C{file_hash}.
        """
        file_path = self._path_from_file_hash(file_hash)
        with open(file_path) as file:
            return file.read()
        
    def put(self, file_data, file_info):
        """
        Almacena un nuevo archivo en este servidor del sistema de 
        archivos distribuidos.
        
        @type file_data: C{str}
        @param file_data: Contenido del archivo que se quiere almacenar.
        
        @type file_info: C{dict}
        @param file_info: Diccionario con los metadatos del archivo.         
        """
        # Save the file in the files directory.
        file_name, file_hash = file_info['name'], file_info['hash']
        file_path = os.path.join(self._files_dir, os.path.sep.join(file_hash[0:5]), file_name)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        with open(file_path, 'w') as file:
            file.write(file_data)

        # Add the metadata of the file to the index.
        file_path = file_path[len(self._files_dir) + 1:]
        writer = self._index.writer()
        writer.delete_by_term('hash', file_hash.decode('utf-8'))
        writer.add_document(
            hash=file_info['hash'].decode('utf-8'),
            tags=u' '.join([tag.decode('utf-8') for tag in file_info['tags']]),
            description=file_info['description'].decode('utf-8'),
            name=file_info['name'].decode('utf-8'),
            size=file_info['size'].decode('utf-8'),
            path=file_path.decode('utf-8'),
        )               
        writer.commit()

        # Update the empty space of this server.
        self._status['empty_space'] -= long(file_info['size'])
        
    def remove(self, file_hash):
        """
        Elimina un archivo almacenado en este servidor.
        
        @type file_hash: C{str}
        @param file_hash: Hash del contenido del archivo que se quiere
            eliminar. Este hash identifica al archivo únicamente
            dentro del sistema de ficheros distribuidos.
        """
        file_path = self._path_from_file_hash(file_hash)
        os.remove(file_path)
        writer = self._index.writer()
        writer.delete_by_term('hash', file_hash.decode('utf-8'))
        writer.commit()
        
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
        
    def search(self, text):
        """
        Realiza una búsqueda de texto libre en los tags y en las descripciones
        de los archivos almacenados en este servidor.
        
        @type text: C{str}
        @param text: Texto de la búsqueda que se quiere realizar.
        
        @rtype: C{set}
        @return: Conjunto con los hash de los archivos que son relevantes 
            para la búsqueda de texto libre C{text}.
        """
        # parser = whoosh.qparser.MultifieldParser(['tags', 'name', 'description'], schema=self._schema)

                
    def info(self, file_hash):
        """
        Obtiene información a partir del hash de un archivo.
        
        @type file_hash: C{str}
        @param file_hash: Hash del contenido del archivo cuya información
            se quiere obtener. Este hash identifica al archivo únicamente
            dentro del sistema de ficheros distribuidos.
            
        @rtype: C{dict}
        @return: Diccionario con los metadatos del archivo.
        """
        
    def terminate(self):
        """
        Este método es utilizado por la instancia de la clase C{TagFSServer} para
        indicar que va a dejar de estar disponible en la red este servidor y que
        se deben guardar todos los recursos abiertos.
        """
        self._index.close()
