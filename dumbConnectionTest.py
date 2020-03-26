#!/usr/bin/env python

import socket
import ssl

TCP_IP = '127.0.0.1'
TCP_PORT = 2080
HOSTNAME = 'localhost'
BUFFER_SIZE = 1024

# Create a simple list of integers to be the message
list = [1, 1, 192, 9, 33, 202, 192, 131, 18, 111]
#list = [1, 1, 64, 73, 14, 86]

# Convert it to bytes
message = bytearray( list )

# Create the socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect and send message
s.connect( (TCP_IP, TCP_PORT) )
s.send( message )
s.close()
