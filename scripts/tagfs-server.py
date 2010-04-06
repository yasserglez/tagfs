#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para ejecutar un servidor TagFS desde la línea de comandos.
"""

import os
import sys
import optparse

# Add to the Python path the directory containing the packages in the source distribution. 
PACKAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'packages'))
sys.path.insert(0, PACKAGES_DIR)

from tagfs import  __version__, __authors__
from tagfs.server import TagFSServer


EXIT_SUCCESS, EXIT_FAILURE = 0, 1


def _parse_args(argv):
    """
    Reconoce las opciones especificadas como argumentos al ejecutar el script
    en la línea de comandos.
    
    @type argv: C{list}
    @param argv: Lista de argumentos del programa.
    
    @rtype: C{tuple}
    @return: Retorna una tupla donde el primer elemento es una estructura
        que almacena la información acerca de las opciones especificadas
        y el segundo elemento es una lista con el resto de los argumentos
        que no se reconocieron como opciones.
    """
    usage = '%prog [options]'
    version = '%%prog (TagFS) v%s\n' % __version__
    authors = '\n'.join(['Copyright (C) 2010 %s' % a for a in __authors__])
    desc = 'Server of the tag-based distributed filesystem.'
    parser = optparse.OptionParser(usage=usage, version=version + authors, 
                                   description=desc, prog=os.path.basename(argv[0]))
    parser.add_option('-i', '--ip', action='store', dest='address', type='string', metavar='IP',
                      help='the IP address of the interface where the TagFS server ' \
                           'should listen for incoming connections')
    options, args = parser.parse_args(args=argv[1:])
    if not options.address:
        parser.error('missing required --ip option')
    return options, args


def main(argv):
    """
    Función principal del script.
    
    @type argv: C{list}
    @param argv: Lista de argumentos del programa.
    
    @rtype: C{int}
    @return: Retorna 0 si no ocurrió ningún error durante la ejecución 
        del programa y 1 en el caso contrario.
    """
    options, args = _parse_args(argv)
    server = TagFSServer(options.address)
    server.start()
    return EXIT_SUCCESS


if __name__ == '__main__':
    sys.exit(main(sys.argv))
