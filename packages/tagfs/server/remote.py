# -*- coding: utf-8 -*-

"""
Implementación del servidor TagFS compartido en la red.   
"""

from tagfs.contrib.Pyro import core


class RemoteTagFSServer(core.ObjBase):
    """
    Servidor TagFS compartido en la red utilizando Pyro. 
    """

    def __init__(self):
        """
        Inicializa una instancia de un servidor TagFS compartido en la red.
        Ejecuta el método encardado de inicializar los aspectos relacionados 
        con Pyro que garantiza que los métodos de esta clase puedan ser
        ejecutados por los clientes TagFS. 
        """
        super(RemoteTagFSServer, self).__init__()
