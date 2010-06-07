# -*- coding: utf-8 -*-

"""
Clases representando una forma de obtener la fecha y hora actual.
"""

import time

import ntplib


class TimeProvider(object):
    """
    Representanda una forma de obtener la fecha y hora actual.
    """
    
    def get_time(self):
        """
        Retorna un identificador del tiempo actual en GMT.
        
        @rtype: C{float}
        @return: Cantidad de segundos transcurridos desde la época.
        """


class LocalTimeProvider(TimeProvider):
    """
    Permite obtener la fecha y hora actual, basado en el reloj local del sistema.
    """
    
    def get_time(self):
        """
        Retorna un identificador del tiempo actual en GMT.
        
        @rtype: C{float}
        @return: Cantidad de segundos transcurridos desde la época.        
        """
        return float(time.mktime(time.gmtime()))

    
class NTPTimeProvider(TimeProvider):
    """
    Permite obtener la fecha y hora actual, a partir de un servidor de NTP.
    """
    
    def __init__(self, ntp_server):
        """
        Permite obtener la fecha y hora actual, a partir de un servidor de NTP.
        
        @type ntp_server: C{str}
        @para ntp_server: Host del servidor NTP.        
        """
        self._server = ntp_server
        self._client = ntplib.NTPClient()
    
    def get_time(self):
        """
        Retorna un identificador del tiempo actual en GMT, obtenido del servidor NTP.
        
        @rtype: C{float}
        @return: Cantidad de segundos transcurridos desde la época.
        """
        response = self._client.request(self._server, version=3)
        return float(response.ref_time)
