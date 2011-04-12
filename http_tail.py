#!/bin/python

from optparse import OptionParser

import commands
import linecache
import BaseHTTPServer
import re
import os
import sys

HTTP_TAIL_GET_FILE_SIZE_CMD = 'wc -l %s | cut -d \' \' -f1'

HTTP_TAIL_TAIL_CMD = 'tail -%d %s'

HTTP_TAIL_VIEW_TEMPLATE = 'view.html'

class HTTPTailRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
   
    def do_GET(self):
        tokens = self.path.split('/')[1:] # Ignoring first, empty element

        command = tokens[0]

        try:
            if command == 'view':
                if self.server.template_data is None:
                    self.server.template_data = ''

                    for line in open(HTTP_TAIL_VIEW_TEMPLATE):
                        self.server.template_data += line.replace('HOST_ADDRESS', '%s:%d' % \
                                                                  self.server.server_address)
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                self.wfile.write(self.server.template_data)
            elif command == 'tail':
                filename = tokens[1]
                start = int(tokens[2])
                file_len = int(commands.getoutput(HTTP_TAIL_GET_FILE_SIZE_CMD % filename))
                tail_len = file_len - start

                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
    
                if filename == self.server.watched_file:
                    data = commands.getoutput('tail -%d %s' % (tail_len, self.server.watched_file))
                    self.wfile.write(data)
        except ValueError:
            self.send_response(400) # Bad request
            self.end_headers()
            raise
            
if __name__ == '__main__':
    filename = sys.argv[1]
    ip = sys.argv[2]
    port = int(sys.argv[3])

    if not os.path.exists(filename):
        print "File not found: %s" % filename
        exit(1)

    server_address = (ip, port)

    httpd = BaseHTTPServer.HTTPServer(server_address, HTTPTailRequestHandler)
    httpd.watched_file = filename
    httpd.template_data = None
    httpd.serve_forever() 
