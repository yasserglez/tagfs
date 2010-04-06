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

    def __init__(self, address):
        """
        Inicializa el cliente TagFS para la línea de comandos.
        """
        super(CLITagFSClient, self).__init__(address)
        
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
