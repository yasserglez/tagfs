# -*- coding: utf-8 -*-

"""
Implementación de un cliente TagFS para la línea de comandos.
"""

import shlex
import textwrap

try:
    # Used by raw_input for history, if available.
    import readline
except ImportError:
    # Ignore this exception on Windows platforms.
    pass

from tagfs.client import TagFSClient
from tagfs import __version__


class CLITagFSClient(TagFSClient):
    """
    Client TagFS para línea de comandos. 
    
    Este cliente emula el funcionamiento de un sistema de ficheros tradicional.
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
        self._continue = True
        self._cwd = '/'
        
    def start(self):
        """
        Inicializa el ciclo principal del cliente TagFS para la línea de comandos.
        """
        welcome = 'Welcome to TagFS v{version}.\n' 
        print welcome.format(version=__version__)
        while self._continue:
            try:
                prompt = 'TagFS:{cwd}> '.format(cwd=self._cwd)
                user_input = raw_input(prompt)
                cmd = user_input.split()[0]
                try:
                    func = getattr(self, '_command_{cmd}'.format(cmd=cmd))
                    args = shlex.split(user_input[len(cmd):].lstrip())
                    func(args)
                except AttributeError:
                    print '\nInvalid command "{cmd}".\n'.format(cmd=cmd)
            except (EOFError, KeyboardInterrupt):
                print 'exit'
                self._command_exit('')
            
    def put(self, name, description, tags, data):
        """
        Añade un nuevo archivo al sistema de ficheros distribuido. Para 
        obtener información acerca de los parámetros de este método consulte 
        la documentación del método C{put} de la clase C{TagFSClient}.
        """
        return super(CLITagFSClient, self).put(name, description, tags, data, 
                                               self._replication)

    def _command_exit(self, args):
        """
        Usage: exit
        
        Ends the execution of the client.
        """
        self.terminate()
        self._continue = False
        
    def _command_help(self, args):
        """
        Usage: help [command]
        
        Prints information about the usage of a command. If it is executed
        without a command as argument it prints the available commands.
        """
        if not args:
            cmds = []
            for attr in dir(self):
                if attr.startswith('_command_'):
                    cmds.append(attr[len('_command_'):])
            single_line = 'Available commands: {cmds}.'.format(cmds=', '.join(cmds))
            multiple_lines = textwrap.wrap(single_line)
            print '\n{msg}\n'.format(msg='\n'.join(multiple_lines))
        else:
            try:
                func = getattr(self, '_command_{cmd}'.format(cmd=args[0]))
                print textwrap.dedent(func.__doc__)
            except AttributeError:
                print '\nInvalid command "{cmd}".\n'.format(cmd=args[0])
