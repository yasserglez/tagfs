# -*- coding: utf-8 -*-

"""
Implementación de un cliente TagFS para la línea de comandos.
"""

import time

from tagfs.client import TagFSClient


class CLITagFSClient(TagFSClient):
    """
    Client TagFS para línea de comandos.
    """

    def __init__(self, address, replication):
        """
        Inicializa el cliente TagFS para la línea de comandos. Consulte
        la documentación del método C{__init__} de la clase C{TagFSClient}
        para obtener información acerca del resto de los parámetros de 
        este método.
        
        @type replication: C{int} 
        @param replication: Porciento de replicación en el sistema de ficheros
            que se debe utilizar para los nuevos archivos añadidos utilizando 
            este cliente de TagFS.        
        """
        super(CLITagFSClient, self).__init__(address)
        self._replication = replication
        
    def start(self):
        """
        Inicializa el ciclo principal del cliente TagFS para la línea de comandos.
        """
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            # Ignore CTRL-C so it can be used to stop the client.
            pass
        finally:
            self.terminate()
            
    def put(self, name, description, tags, data):
        """
        Añade un nuevo archivo al sistema de ficheros distribuido. Para 
        obtener información acerca de los parámetros de este método consulte 
        la documentación del método C{put} de la clase C{TagFSClient}.
        """
        super(CLITagFSClient, self).put(name, description, tags, data, 
                                        self._replication)
