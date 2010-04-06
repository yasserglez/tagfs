# -*- coding: utf-8 -*-

import subprocess


FETCH_CMD = ['git', 'fetch', 'origin']

MERGE_CMD = ['git', 'merge', 'origin/master']

PUSH_CMD = ['git', 'push', 'origin', 'master']


def main():
    """
    Función principal del script.
    """
    subprocess.call(FETCH_CMD)
    subprocess.call(MERGE_CMD)
    subprocess.call(PUSH_CMD)


if __name__ == '__main__':
    main()