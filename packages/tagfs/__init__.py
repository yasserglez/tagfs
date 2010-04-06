# -*- coding: utf-8 -*-

"""
Paquete principal de TagFS, un sistema de ficheros distribuidos basado en tags.
"""

import os
import sys


# Add the contrib directory to the Python path.
contrib_dir = os.path.join(os.path.dirname(__file__), 'contrib')
sys.path.insert(0, os.path.abspath(contrib_dir))


__version__ = '0.1'

__authors__ = (
    'Abel Puentes Luberta <abelchino@lab.matcom.uh.cu>',
    'Andy Venet Pompa <vangelis@lab.matcom.uh.cu>',
    'Ariel Hernández Amador <gnuaha7@uh.cu>',
    'Yasser González Fernández <yglez@uh.cu>',
)
