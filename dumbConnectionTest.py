#!/usr/bin/env python

import socket
import ssl

TCP_IP = '127.0.0.1'
TCP_PORT = 2080
HOSTNAME = 'localhost'
BUFFER_SIZE = 1024

# Create a simple list of integers to be the message
list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
# Convert it to bytes
message = bytearray( list )

# Create the socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Wrap it with SSL
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.load_default_certs()
ws = ssl_context.wrap_socket( s, server_hostname=HOSTNAME )

# Connect and send message
ws.connect( (TCP_IP, TCP_PORT) )
ws.send( message )
ws.close()

