# -*- coding: utf-8 -*-

"""
Implementación de un cliente TagFS para la línea de comandos.
"""

import shlex
import textwrap
from io import open

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
        self._user = "foo"
        self._group = "foo"
        self._description = "Uploaded from Command Line Client"
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
            
    def put(self, name, description, tags, owner, group, perms, data):
        """
        Añade un nuevo archivo al sistema de ficheros distribuido. Para 
        obtener información acerca de los parámetros de este método consulte 
        la documentación del método C{put} de la clase C{TagFSClient}.
        """
        return super(CLITagFSClient, self).put(name, description, tags, owner,
                                               group, perms, data, self._replication)

    def _get_file_hash(self, path):
        """
        Devuelve el identificador del sistema correspondient al archivo del path.
        """
        path = self._get_absolute(path)
        tags = self._get_tags(path)
        file_hash = self.list(tags).index(path.split("/")[-1])
        return file_hash
    
    def _get_absolute(self, path):
        """
        Devuelve el camino absoluto a partir de un camino no necesariamente 
        absoluto.
        
        En caso de que path sea en efecto un camino absoluto no hace nada. 
        """
        if not path.startswith("/"):
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
    
    def _command_cp(self, args):
        """
        Usage: cp [source:]file1 [source:]file2
        
        Copies the content of file1 into file2. 
        Sources available are "local" for local files and "remote" for files 
        into TagFS. The default source is "remote".  
        """
        
        error_msg = '{command}: {msg}.'
        if (not args) or (len(args) < 2):
            print error_msg.format(command='cp', msg='Missing operand')
            print 'Try "help {command}" for more information.'.format(command='mkdir')
            return
        #file1
        file1 = None
        local_file1, local_file2 = None, None
        if args[0].startswith("local:"):
            try:
                local_file1 = open(args[0][6:], 'rb')
                file1 = local_file1.read()
            except Exception:
                print error_msg.format(command='cp', 
                                       msg='Unable to access {0}'.format(args[0]))
        else:
            if args[0].startswith("remote:"):
                path = args[0][7:]
            else:
                path = args[0]
                path = self._get_absolute(path)
                
            name = path[path.rfind('/')+1:]
            path_tags = self._get_tags(path)
            infos = [self.info(hash) for hash in self.list(path_tags)]
            file_hash = None
            for info in infos:
                if info['name'] == name:
                    file_hash = info['hash']
                    break
            if not file_hash:                   
                print error_msg.format(command='cp', 
                                       msg='Unable to access {0}'.format(args[0]))
            else:
                file1 = self.get(file_hash)
        
        #write file1 into file2.
        if args[1].startswith("local:"):
            try:
                local_file2 = open(args[1][6:], 'wb')
                local_file2.write(file1)
            except Exception:
                print error_msg.format(command='cp', 
                                       msg='Unable to access {0}'.format(args[1]))
        else:
            if args[1].startswith("remote:"):
                path = args[1][7:]
            else:
                path = args[1]
                path = self._get_absolute(path)
            name = path[path.rfind('/')+1:]
            path_tags = self._get_tags(path)

            try:
                self.put(name, self._description, path_tags, self._user, 
                         self._group, 775, file1)
                self._empty_dirs.difference_update(path_tags)
            except Exception:
                print error_msg.format(command='cp', 
                                       msg='Unable to access {0}'.format(args[1]))
                        
    def _command_rm(self, args):
        """
        Usage: rm file
        
        Removes the file of the system.
        """
        print self.list(args)
    
    def _command_cd(self, args):
        """
        Usage: cd [directory]
        
        Changes the current directory. If it is executed without a directory
        as arguments it changes the current directory for /.
        """ 
        error_msg = '{command}: {file}: {msg}.'
        path = ""
        path_tags = set() 
        if not args:
            path = "/"
        elif args[0] == "..":
            index = self._cwd[:-1].rindex('/')
            path = self._cwd[:index+1]
            path_tags = self._get_tags(path)
        else:
            if not args[0].endswith('/'):
                args[0] = args[0]+'/'
            path = self._get_absolute(args[0])
            path_tags = self._get_tags(path)
        
        all_tags = self.get_all_tags()
        
        if (path == '/' or 
            (len(self._empty_dirs) > 0 and 
             (path_tags - all_tags).issubset(self._empty_dirs))):
            self._cwd = path
        else:
            infos = [self.info(hash) for hash in self.list(path_tags)]
            if not infos:
                print error_msg.format(command='cd', file=args[0], 
                                       msg='Not such file or directory')
            else:
                self._cwd = path

    def _command_mkdir(self, args):
        """
        Usage: mkdir directory
        
        Creates the directory if not exists.
        """
        error_msg = '{command}: {msg}.'
        if not args:
            print error_msg.format(command='mkdir',msg='Missing operand')
            print 'Try "help {command}" for more information.'.format(command='mkdir')
        else:
            if not args[0].endswith('/'):
                args[0] = args[0]+'/'
            path = self._get_absolute(args[0])
            dir_name_index = path[:-1].rindex('/')
            dir_name = path[dir_name_index+1:-1]
            path = path[:dir_name_index]
            tags = self._get_tags(path)
            all_tags = self.get_all_tags()
            all_dirs = (all_tags | self._empty_dirs)
            
            if tags.issubset(all_dirs):
                if dir_name in all_dirs:
                    msg = error_msg.format(command='mkdir',msg=' Cannot create directory {file}: {reason}')
                    msg = msg.format(file=dir_name, reason='File exists')
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
        elements = {}
        error_msg = '{command}: {file}: {msg}.'
        if not args:
            path = self._cwd
        else:
            path = self._get_absolute(args[0])
            
        if path == '/':
            all_tags = self.get_all_tags()
            for dir in all_tags | self._empty_dirs:
                elements[dir] = (None, True)
        else:
            path_tags = self._get_tags(path)
            all_tags = self.get_all_tags()
            tags = set()
            if (len(self._empty_dirs) > 0 and 
                (path_tags - all_tags).issubset(self._empty_dirs)):
                for dir in (self._empty_dirs - (path_tags - all_tags)):
                    elements[dir] = (None, True)
            else:
                infos = [self.info(hash) for hash in self.list(path_tags)]
                if not infos:
                    print error_msg.format(command='cd', file=args[0], 
                                           msg='Not such file or directory')
                else:
                    for info in infos:
                        elements[info['name']] = (info, False)
                        tags |= info['tags']
                    for tag in tags - path_tags:
                        elements[tag] = (None, True)
                    for tag in self._empty_dirs:
                        elements[tag] = (None, True)
        print 'total {0}'.format(len(elements))
        msg = '{perms} {owner} {group} {size} {name}'
        largest = [-1, -1, -1, -1, -1]
        items = []
        for name, (info, dir) in elements.items():
            if dir:
                item = ('drwxr-xr-x', self._user, self._group,
                              '0000', name)
            else:
                item = (str(info['perms']).rjust(10), info['owner'],
                        info['group'], info['size'], info['name'])
            if len(item[0]) > largest[0]:
                largest[0] = len(item[0])
            if len(item[1]) > largest[1]:
                largest[1] = len(item[1])
            if len(item[2]) > largest[2]:
                largest[2] = len(item[2])
            if len(item[3]) > largest[3]:
                largest[3] = len(item[3])
            if len(item[4]) > largest[4]:
                largest[4] = len(item[4])                
            items.append(item)
        for perms, owner, group, size, name in items:
            print msg.format(perms=perms.rjust(largest[0]),
                             owner=owner.rjust(largest[1]),
                             group=group.rjust(largest[2]),
                             size=size.rjust(largest[3]),
                             name=name.rjust(largest[4]))
        
    def _command_find(self, args):
        """
        Usage: find term
        
        Finds into the description, type, tags and name of the files in the 
        system the term provided.
        TODO 
        """
        
    def _command_file(self, args):
        """
        Usage: file file
        
        Determine type of the file.
        TODO    
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
