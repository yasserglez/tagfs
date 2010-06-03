# -*- coding: utf-8 -*-

"""
Clases representando una forma de obtener la fecha y hora actual.
"""

import time


class TimeProvider(object):
    """
    Representanda una forma de obtener la fecha y hora actual.
    """
    
    def get_time(self):
        """
        Retorna un identificador del tiempo actual en GMT.
        
        @rtype: C{float}
        @return: Cantidad de segundos transcurridos desde la epoca.
        """


class LocalTimeProvider(TimeProvider):
    """
    Permite obtener la fecha y hora actual, basado en el reloj local del sistema.
    """
    
    def get_time(self):
        """
        Retorna un identificador del tiempo actual en GMT.
        """
        return float(time.mktime(time.gmtime()))
