# -*- coding: utf-8 -*-

"""
Script para generar documento con la historia de los cambios.
"""

import os
import subprocess

SRC_DIR = os.path.join(os.path.dirname(__file__), os.pardir)

DOCS_DIR = os.path.abspath(os.path.join(SRC_DIR, 'docs'))

TMP_FILE = os.path.join(DOCS_DIR, 'changelog-tmp.tex')

GIT_CMD = ['git', 'log', '--no-merges', '--date-order', '--pretty=format:%ai & %an & %s%n%n%b%n%n \\\\ \\hline']

LATEX_CMD = ['pdflatex', os.path.join(DOCS_DIR, 'changelog.tex')]


def main():
    """
    Función principal del script.
    """
    # Get the content of the file from the output of the git log command.
    os.chdir(SRC_DIR)
    with open(TMP_FILE, 'w') as tmp_file:
        subprocess.call(GIT_CMD, stdout=tmp_file)
    # Escape underscores in the LaTeX file.
    with open(TMP_FILE, 'r+') as tmp_file:
        data = tmp_file.read()
        tmp_file.seek(0)
        data = data.replace(r'_', r'\_')
        data = data.replace(r'<', r'$<$')
        data = data.replace(r'>', r'$>$')
        tmp_file.write(data)
    # Compile the LaTeX file.
    os.chdir(DOCS_DIR)
    for i in xrange(2):
        subprocess.call(LATEX_CMD)
    for f in os.listdir(DOCS_DIR):
        if f.startswith('changelog') and f not in ('changelog.tex', 'changelog.pdf'):
            os.remove(os.path.join(DOCS_DIR, f))        

    
if __name__ == '__main__':
    main()
