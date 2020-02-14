#!/usr/bin/env python3
import argparse
import sys
import socket
from socket import socket as Socket
import ssl
import threading



CERT_PATH = "/mnt/c/Users/gearl/Desktop/LoRaMessenger/ProxyServer/cert.pem"



def main():
    # Default to port 2080
    args = 2080
    
    # If arguments are present, use them to determine port 
    if len(sys.argv) > 1:
        args = int(sys.argv[1])
    
    # Create the server socket (to handle tcp requests using ipv4), make sure
    # it is always closed by using with statement.
    # SOCK_STREAM - sets up the socket to use the TCP transfer protocol
    with Socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        
        # The socket stays connected even after this script ends. So in order
        # to allow the immediate reuse of the socket (so that we can kill and
        # re-run the server while debugging) we set the following option. This
        # is potentially dangerous in real code: in rare cases you may get junk
        # data arriving at the socket.
        
        # Set socket options
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the socket to the given port
        try:
            server_socket.bind( ('', args) )
        except socket.error as error:
            print( str(error) )

        # Have the socket listen
        try:
            server_socket.listen()
        except socket.error as error:
            print( str(error) )

        # Create an ssl context to wrap the socket in 
        ssl_context = ssl.create_default_context( ssl.Purpose.CLIENT_AUTH )

        # Load a set of default certification authority certificates from
        # default locations to authenticate client connects to the proxy server
        ssl_context.load_cert_chain( certfile=CERT_PATH )

        ssl_context.set_ciphers('EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH')

        # Wrap the socket to get an SSL socket
        wrapped_socket = ssl_context.wrap_socket( server_socket, server_side=True )

        print( "Proxy server ready" )
        print( "Main server loop is running on thread " + str(threading.get_ident()) )
        
        while True:

            # Accept an incomming message
            connected_socket = wrapped_socket.accept()[0]

            connected_stream = ssl_context.wrap_socket( connected_socket, server_side=True )

            # Save the received message as ascii
            # .decode() uses utf-8 by default
            message = connected_socket.recv(1024)

            # Spool off a new thread to handle the message
            new_thread = message_handler_thread( message )

            # Start the new thread
            new_thread.start()
            
    return 0



class message_handler_thread(threading.Thread):
    def __init__(self, message):
        threading.Thread.__init__(self)
        self.message = message

    def run(self):
        print( "Starting thread " + str(threading.get_ident()) )
        self.handleMessage( self.message )
        print( "Exiting thead " + str(threading.get_ident()) )

    def handleMessage(self, message):
        print( "handle message began" )

        # TODO: Handle any kind of header metadata that gets added to the bytes
        # for the transmission from the gateway to the proxy server

        # Convert the string of bytes into an array of bytes
        byteArray = list( message )

        # Retrieve the app and api bytes
        appNameByte = byteArray[0]
        apiNameByte = byteArray[1]

        # Read the appropriate encoding table based upon the app/api combo
        self.readEncodingTable(appNameByte, apiNameByte)

        # Iterate through remaining bytes
        for index in range(2, len(byteArray)):
            
            # Decode each byte
            self.decodeFromTable( byteArray[index] )

        # Send the composed message off to its destination
        self.forwardMessage()

    def readEncodingTable(self, appName, apiName):
        print( "readEncodingTable ran; app: " + str(appName) + " api: " + str(apiName) )

        

    def decodeFromTable(self, byteCode):
        print( "decodeFromTable ran on " + str(byteCode) )

    def forwardMessage(self):
        print( "forwardMessage ran" )



if __name__ == "__main__":
    sys.exit(main())
