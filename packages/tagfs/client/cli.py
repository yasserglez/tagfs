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
        all_tags = self.get_all_tags() 
        self._cwd_elements = dict(zip(all_tags,len(all_tags)*[(None,True)]))
        self._empty_dirs = set()
        
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

    def _get_absolute(self, path):
        """
        Devuelve el camino absoluto a partir de un camino no necesariamente 
        absoluto.
        
        En caso de que path sea en efecto un camino absoluto no hace nada. 
        """
        if not path.startwith("/"):
            return self._cwd + path
        else:
            return path
        
    def _get_tags(self, path):
        """
        Construye el conjunto de tags que representa un camino absoluto.
        """
        list = path.split("/")[1:]
        if not path.endswith("/"):
            list = list[:-1]
        return set(list)-set([''])        
        
    def _command_rm(self, args):
        """
        Usage: rm file
        
        Removes the file of the system.
        """
    
    def _command_cd(self, args):
        """
        Usage: cd [directory]
        
        Changes the current directory. If it is executed without a directory
        as arguments it changes the current directory for /.
        """ 
        error_msg = '{command}: {file}: {msg}.'.format(command='cd') 
        if not args:
            self._cwd = "/"
            all_tags = self.get_all_tags() 
            self._cwd_elements = dict(zip(all_tags,len(all_tags)*[(None,True)]))
        else:
            cwd_elements = {}
            if not args[0].endswith('/'):
                args[0] = args[0]+'/'
            path = self._get_absolute(args[0])
            path_tags = self._get_tags(path)
            all_tags = self.get_all_tags()
            if (path_tags - all_tags).issubset(self._empty_dirs):
                self._cwd = path
                self._cwd_elements = cwd_elements
            else:
                tags = set(path_tags)
                infos = [self.info(hash) for hash in self.list(path_tags-self._empty_dirs)]
                if not infos:
                    print error_msg.format(file=args[0], 
                                           msg='Not such file or directory')
                else:
                    for info in infos:
                        cwd_elements[info['name']] = (info, False)
                        tags |= info['tags']
                    for tag in tags - path_tags:
                        cwd_elements[tag] = (None, True)
                    self._cwd = path
                    self._cwd_elements = cwd_elements
    
    def _command_mkdir(self, args):
        """
        Usage: mkdir directory
        
        Creates the directory if not exists.
        """
        error_msg = '{command}: {msg}.'.format(command='mkdir')
        if not args:
            print error_msg.format(msg='Missing operand')
            print 'Try "help {command}" for more information.'.format(command='mkdir')
        else:
            if not args[0].endswith('/'):
                args[0] = args[0]+'/'
            dir_name_index = args[0][:-1].rindex('/')
            dir_name = args[0][dir_name_index:-1]
            path = self._get_absolute(args[0][:dir_name_index+1])
            tags = self._get_tags(path)
            all_tags = self.get_all_tags()
            all_dirs = (all_tags | self._empty_dirs)
            if tags.issubset(all_dirs):
                if dir_name in all_dirs:
                    msg = error_msg.format(msg=' Cannot create directory {file}: {reason}')
                    msg = msg.format(file=args[0], reason='File exists')
                    print msg
                else: 
                    self._empty_dirs.add(dir_name)
            else:
                msg = error_msg.format(msg=' Cannot create directory {file}: {reason}')
                msg = msg.format(file=args[0], reason='Not such file or directory')
                print msg
        
    def _command_ls(self, args):
        """
        Usage: ls [directory]
        
        Lists the content of the directory. If it is executed without a 
        directory as argument it prints the content of the current directory. 
        """
        
    def _command_find(self, args):
        """
        Usage: find term
        
        Finds into the description, type, tags and name of the files in the 
        system the term provided. 
        """
        
    def _command_file(self, args):
        """
        Usage: file file
        
        Determine type of the file.        
        """

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
