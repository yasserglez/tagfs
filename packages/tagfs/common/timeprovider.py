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
    
class NtpTimeProvider(TimeProvider):
    """
    Permite obtener la fecha y hora actual, a partir de un servidor de NTP.
    """
    
    def __init__(self, ntp_server):
        """
        Permite obtener la fecha y hora actual, a partir de un servidor de NTP.
        """
        self._server = ntp_server
    
    def get_time(self):
        """
        Retorna un identificador del tiempo actual en GMT, 
        a partir del servidor NTP.
        """
        client = ntplib.NTPClient()
        response = client.request(self._server, version=3)
        return response.ref_time
