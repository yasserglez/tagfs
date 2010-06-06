#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import socket
import subprocess


def get_usable_addrport(host='localhost', port_start=1024, port_end=49151):
    sock = socket.socket()
    addrport = None
    for port in range(port_start, port_end + 1):
        address = (host, port)
        try:
            sock.bind(address)
        except socket.error, error:
            if error.errno == 98:
                pass
        else:
            addrport = '%s:%s' % (host, port)
    sock.close()
    return addrport


def open_browser(root_url):
    try:
        browser_args = ('/usr/bin/xdg-open', root_url)
        subprocess.Popen(browser_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		print 'Opening Canipedia using your default web browser.'
    except OSError:
        print 'Could not open Canipedia using your default web browser.'
        print 'Please, manually visit "%s",' % root_url

def main():
    # Run the Django development server.
    addrport = get_usable_addrport(port_start=8000)
    manage_script = os.path.join(os.path.dirname(__file__), os.pardir, 'django/project/manage.py')
    server_args = ('/usr/bin/python', os.path.abspath(manage_script), 'runserver', addrport)
    server_process = subprocess.Popen(server_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print 'Canipedia is running. You can stop Canipedia using CONTROL-C.'
    # Wait for the Django server to start. Sleep 1 second.
    time.sleep(1)
    # Open the web browser.
    root_url = 'http://%s/' % addrport
    open_browser(root_url)
    # Wait until the Django server exits.
    try:
        server_process.wait()
    except KeyboardInterrupt:
        # Exit process using CONTROL-C.
        pass


if __name__ == '__main__':
    main()
