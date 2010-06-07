#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import socket
import webbrowser
import subprocess


def get_usable_addrport(host='localhost', port_start=1024, port_end=49151):
    sock = socket.socket()
    addrport = None
    for port in xrange(port_start, port_end + 1):
        address = (host, port)
        try:
            sock.bind(address)
            addrport = port
            break
        except socket.error:
            pass
    sock.close()
    return addrport


def open_browser(root_url):
    try:
        webbrowser.open(root_url)
        print 'Opening TagFs using your default web browser.'
    except OSError:
        print 'Could not open TagFs using your default web browser.'
        print 'Please, manually visit "%s",' % root_url

def main():
    # Run the Django development server.
    addrport = get_usable_addrport(port_start=8000)
    manage_script = os.path.join(os.path.dirname(__file__), os.pardir, 'packages/tagfs/client/web/project/manage.py')
    server_args = (sys.executable, os.path.abspath(manage_script), 'runserver', str(addrport))
    server_process = subprocess.Popen(server_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print 'TagFs is running. You can stop TagFs using CONTROL-C.'
    # Wait for the Django server to start.
    time.sleep(5)
    # Open the web browser.
    root_url = 'http://localhost:%s/' % addrport
    open_browser(root_url)
    # Wait until the Django server exits.
    try:
        server_process.wait()
    except KeyboardInterrupt:
        # Exit process using CONTROL-C.
        pass


if __name__ == '__main__':
    main()
