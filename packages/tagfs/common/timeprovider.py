# -*- coding: utf-8 -*-

"""
Código común para la implementación del cliente y el servidor de TagFS.
"""
import time

class TimeProvider(object):
    """
    """
    
    def get_time(self):
        """
        Retorna un identificador del tiempo actual GM.
        
        @rtype: C{float}
        @return: Retorna la cantidad de segundos transcurridos desde la "epoca"
            del sistema.
        """
        
class LocalTimeProvider(TimeProvider):
    """
    Proveedor de tiempo local. 
    Basado en el reloj local del sistema.
    """
    
    def get_time(self):
        """
        """
        return float(time.mktime(time.gmtime()))
    
