#!/usr/bin/env python3
import argparse
import json
import requests
import socket
import ssl
import struct
import sys
import threading



# The number of bytes allocated to an arbitrary float parameter
FLOAT_PARAM_LENGTH = 4
# The number of bytes allocated to an arbitrary double parameter
DOUBLE_PARAM_LENGTH = 8

received_messages = {}


def main():


    # Default to port 2080
    args = 2080

    # If arguments are present, use them to determine port
    if len(sys.argv) > 1:
        args = int(sys.argv[1])

    # Create the server socket (to handle tcp requests using ipv4), make sure
    # it is always closed by using with statement.
    # SOCK_STREAM - sets up the socket to use the TCP transfer protocol
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

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

        while True:
            # Accept an incomming message
            connected_socket = server_socket.accept()[0]

            # Save the received message as ascii
            # .decode() uses utf-8 by default
            #message = connected_socket.recv(1024)
            message = receiveMessage( connected_socket )
            print(f"This is the message built in the loop: {message}")

            # Spool off a new thread to handle the message
            new_thread = message_handler_thread( message )

            # Start the new thread
            new_thread.start()

    return 0


def count_received_fragments(message):
    ''' Counts the number of fragments in a given message '''
    return len(message) // 12


def check_expected_fragments(message):
    ''' Checks the number of expected fragments based on the entry in
    index 2. Accounts for possibility of messages coming out of order '''
    total_number_fragments = message[2]
    while total_number_fragments > 16:
        total_number_fragments -= 16
    return total_number_fragments


def get_app_and_api(message):
    ''' Get's the app and api nibbles from a cleaned messaged '''
    base = 2**4
    byte = message[0]
    app = byte // base
    api = byte - (app * base)
    return (app, api)


def strip_metadata(message):
    ''' Removes metadata from a message.
    Metadata is the UID, Message number, and number of expected messages '''
    total_number_fragments = check_expected_fragments(message)
    if count_received_fragments(message) != total_number_fragments:
        raise Exception 
    ret_list = []
    working_list = message
    for fragments in range(total_number_fragments):
        ret_list.append(working_list[3:13])
        working_list = working_list[13:]
    return rebuild_message(ret_list)


def rebuild_message(message):
    ''' Helper function for strip_metadata.
    Combines all lists created by strip_metadata back into a single list '''
    rebuilt_message = []
    for lists in message:
        for items in lists:
            rebuilt_message.append(items)
    return rebuilt_message


class message_handler_thread(threading.Thread):
    def __init__(self, message):
        threading.Thread.__init__(self)
        self.message = message
        self.appName = None
        self.apiName = None
        self.paramsTable = None

    def run(self):
        print( "Starting thread " + str(threading.get_ident()) )
        self.handleMessage( self.message )
        print( "Exiting thead " + str(threading.get_ident()) )

    def handleMessage(self, message):
        print( "handle message began" )

        #try:
        # TODO: Handle any kind of header metadata that gets added to the bytes
        # for the transmission from the gateway to the proxy server

        # Convert the string of bytes into an array of bytes
        byteArray = list( message )

        # Strip metadata from byte array
        byteArray = strip_metadata(byteArray)

        # Retrieve the app and api bytes
        ( appNameByte, apiNameByte ) =  get_app_and_api(byteArray)
         

        # Read the appropriate encoding table based upon the app/api combo
        self.readDecodingTable(appNameByte, apiNameByte)

        decodedMessage = self.appName + "/" + self.apiName

        # Check if the api has params
        if self.paramsTable:

            decodedMessage += "?"

            # Initialize the byte index at 1 since we already read the first index 
            # bytes
            byteIndex = 1

            # Parse the remaining bytes as the parameters in order
            for parameter in self.paramsTable:

                # Read the name and values of the param
                paramName = parameter[ "name" ]
                paramValues = parameter[ "values" ]

                # Determine behavior based on the type of parameter
                if type(paramValues) is dict:

                    # Decode the parameter using its values hash
                    value = paramValues[ str( byteArray[ byteIndex ] ) ]

                    decodedMessage += paramName + "=" + str( value ) + "&"

                    # Iterate the byteIndex
                    byteIndex += 1

                elif paramValues == "int-param":

                    try:
                        # Retreive the number of bytes dedicated to this integer
                        integerLength = int( parameter[ "length" ] )

                        # Retreive a sub array of the bytes dedicated to this parameter
                        integerSubArray = byteArray[ byteIndex:( byteIndex + integerLength ) ]

                        print( bytes( integerSubArray ) )

                        # Convert the array of bytes into an integers\
                        value = int.from_bytes( integerSubArray, byteorder='big', signed=False)

                        print( value )

                        decodedMessage += paramName + "=" + str( value ) + "&"

                        # Iterate the byteIndex
                        byteIndex += integerLength

                    except IndexError as e :
                        # Catch the index error
                        print( type(e) )
                        print( "Byte missing for int-param" )
                        raise

                elif paramValues == "float-param":

                    try:
                        # Retreive a sub array of the bytes dedicated to this parameter
                        floatSubArray = byteArray[ byteIndex:( byteIndex + FLOAT_PARAM_LENGTH ) ]
                        floatSubArray.reverse()

                        print( bytes( floatSubArray ) )

                        # Convert the array of bytes into a floating point number
                        value = struct.unpack( 'f', bytes( floatSubArray ) )[0]

                        print( value )

                        decodedMessage += paramName + "=" + str( value ) + "&"

                        # Iterate the byteIndex
                        byteIndex += FLOAT_PARAM_LENGTH

                    except IndexError as e :
                        # Catch the index error
                        print( type(e) )
                        print( "Byte missing for float-param" )
                        raise

                elif paramValues == "double-param":

                    try:
                        # Retreive a sub array of the bytes dedicated to this parameter
                        doubleSubArray = byteArray[ byteIndex:( byteIndex + DOUBLE_PARAM_LENGTH ) ]
                        doubleSubArray.reverse()

                        print( bytes( doubleSubArray ) )

                        # Convert the array of bytes into a floating point number
                        value = struct.unpack( 'd', bytes( doubleSubArray ) )[0]

                        print( value )

                        decodedMessage += paramName + "=" + str( value ) + "&"

                        # Iterate the byteIndex
                        byteIndex += DOUBLE_PARAM_LENGTH

                    except IndexError as e :
                        # Catch the index error
                        print( type(e) )
                        print( "Byte missing for double-param" )
                        raise


                elif paramValues == "char-param":

                    try:
                        # Retreive the number of bytes dedicated to this integer
                        charLength = int( parameter[ "length" ] )

                        # Retreive a sub array of the bytes dedicated to this parameter
                        charSubArray = byteArray[ byteIndex:( byteIndex + charLength ) ]

                        # Convert the array of bytes into an integers\
                        value = int.from_bytes( charSubArray, byteorder='big', signed=False)

                        value = chr( value )

                        decodedMessage += paramName + "=" + str( value ) + "&"

                        # Iterate the byteIndex
                        byteIndex += charLength

                    except IndexError as e :
                        # Catch the index error
                        print( type(e) )
                        print( "Byte missing for int-param" )
                        raise

            # Trim trailing "&"
            decodedMessage = decodedMessage[:-1]

        # TODO: Handle remaining bytes in some way, potentially a checksum?

        # Send the composed message off to its destination
        self.forwardMessage( decodedMessage )

        # except Exception as e:
        #     print( type(e) )
        #     print( "thread was unable to handle the message" )

    def readDecodingTable(self, appByte, apiByte):
        print( "readDecodingTable ran; app: " + str(appByte) + " api: " + str(apiByte) )

        try:
            # Open the encoding table file and convert it into a dictionary
            file = open("decoding_table.json", 'r')
            decodingTable = json.load(file)

        except FileNotFoundError as e:
            # Catch file not found exception,
            print( type(e) )
            print( "No encoding table found" )
            raise

        try:
            # Attempt to read the application name
            appTable = decodingTable[ str(appByte) ]

        except KeyError as e:
            # Catch key error
            print( type(e) )
            print( "App byte not found in decoding table" )
            raise

        try:
            # Attempt to read the api name
            apiTable = appTable[ str(apiByte) ]

        except KeyError as e :
            # Catch key error
            print( type(e) )
            print( "API byte not found in decoding table" )
            raise

        try:
            # Save the application's url
            self.appName = appTable[ "url" ]

            # Save the api name
            self.apiName = apiTable[ "name" ]

            # Save the api's parameters
            self.paramsTable = apiTable[ "params" ]

        except KeyError as e :
            # Catch key error
            print( type(e) )
            print( "Decoding table missing information" )
            raise

    def forwardMessage(self, message):
        print( "forwardMessage ran" )
        print( message )

        # Potentially use request to send the message off with its data?



def receiveMessage( socket ):
    rawMessageLength = receiveAll( socket, 4 )

    if not rawMessageLength:
        return None
    messageLength = struct.unpack('>I', rawMessageLength)[0]

    return receiveAll( socket, messageLength )

def receiveAll( socket, n ):
    data = bytearray()
    while len(data) < n:
        packet = socket.recv( n - len(data) )
        if not packet:
            return None
        data.extend( packet )
    return data
if __name__ == "__main__":
    sys.exit(main())
