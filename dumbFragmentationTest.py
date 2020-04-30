#!/usr/bin/env python

import socket
import ssl
import time

TCP_IP = '127.0.0.1'
TCP_PORT = 2080
HOSTNAME = 'localhost'
BUFFER_SIZE = 1024

# Create a simple list of integers to be the message
list = [17, 3, 17, 64, 40, 160, 196, 155, 165, 227, 84, 64, 43]

# Convert it to bytes
message1 = bytearray( list )

# Create a simple list of integers to be the message
list = [17, 19, 32, 196, 155, 165, 227, 84, 46, 9, 63, 1,  17]

# Convert it to bytes
message2 = bytearray( list )

# Create a simple list of integers to be the message
list = [17, 35, 77, 228, 80, 96, 94, 227]

# Convert it to bytes
message3 = bytearray( list )

# Create the socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect and send message
s.connect( (TCP_IP, TCP_PORT) )
s.send( message1 + message2 + message3 )
s.close()

#
# time.sleep( 2 )
#
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
# s.connect( (TCP_IP, TCP_PORT) )
# s.send( message1 )
# s.close()
#
# time.sleep( 2 )
#
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
# s.connect( (TCP_IP, TCP_PORT) )
# s.send( message3 )
# s.close()
