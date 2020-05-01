#!/usr/bin/env python3
import argparse
import json
import socket
import struct
import sys
import threading



# The number of bytes allocated to an arbitrary float parameter
FLOAT_PARAM_LENGTH = 4
# The number of bytes allocated to an arbitrary double parameter
DOUBLE_PARAM_LENGTH = 8



def main():
    ''' Main function responsible for running the basic server loop. '''

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
            message = receive_message( connected_socket )
            print(f"This is the message built in the loop: {list( message )}")

            # Spool off a new thread to handle the message
            new_thread = message_handler_thread( message )

            # Start the new thread
            new_thread.start()

    return 0



class message_handler_thread(threading.Thread):
    ''' Thread class responsible for handling a single message. '''

    def __init__(self, message):
        threading.Thread.__init__(self)
        self.message = message


    def run(self):
        print( "Starting thread " + str(threading.get_ident()) )
        self.handle_message( self.message )
        print( "Exiting thead " + str(threading.get_ident()) )


    def handle_message( self, message ):
        ''' Decodes the given message based on the information found in
            decoding_table.json, then forwards the message to its intended
            destination. '''
        print( "handle message began" )
        # Convert the string of bytes into an array of bytes
        byte_array = list( message )

        # Strip metadata from byte array
        byte_array = strip_metadata(byte_array)
        print( byte_array )

        # Retrieve the app and api bytes
        ( app_name_byte, api_name_byte ) =  get_app_and_api( byte_array )

        # Read the appropriate encoding table based upon the app/api combo
        # Default to reading from "decoding_table.json"
        ( app_name, api_name, params_table ) = read_decoding_table( "decoding_table.json", app_name_byte, api_name_byte )

        # Decode the message
        decoded_message = decode_message( app_name, api_name, params_table, byte_array )

        # Send the composed message off to its destination
        forward_message( decoded_message )


def read_decoding_table( filename, app_byte, api_byte ):
    ''' Reads the file decoding_table.json and parses it to determine the
        name of the app that sent the message, the name of the api the
        message is using, and a list of parameters to expect with the
        message. '''
    print( "read_decoding_table ran; app: " + str(app_byte) + " api: " + str(api_byte) )

    try:
        # Open the encoding table file and convert it into a dictionary
        file = open( filename, 'r')
        decoding_table = json.load(file)

    except FileNotFoundError as e:
        # Catch file not found exception,
        print( type(e) )
        print( "No encoding table found" )
        raise

    try:
        # Attempt to read the application name
        app_table = decoding_table[ str(app_byte) ]

    except KeyError as e:
        # Catch key error
        print( type(e) )
        print( "App byte not found in decoding table" )
        raise

    try:
        # Attempt to read the api name
        api_table = app_table[ str(api_byte) ]

    except KeyError as e :
        # Catch key error
        print( type(e) )
        print( "API byte not found in decoding table" )
        raise

    try:
        # Return the application's url, the api name, and the api's parameters
        return( app_table[ "url" ], api_table[ "name" ], api_table[ "params" ] )

    except KeyError as e :
        # Catch key error
        print( type(e) )
        print( "Decoding table missing information" )
        raise


def decode_message( app_name, api_name, params_table, byte_array ):
    decoded_message = app_name + "/" + api_name

    # Check if the api has params
    if params_table:

        decoded_message += "?"

        # Initialize the byte index at 1 since we already read the first index
        # bytes
        byte_index = 1

        # Parse the remaining bytes as the parameters in order
        for parameter in params_table:

            # Read the name and values of the param
            param_name = parameter[ "name" ]
            param_values = parameter[ "values" ]

            # Determine behavior based on the type of parameter
            if type(param_values) is dict:

                # Decode the parameter using its values hash
                value = param_values[ str( byte_array[ byte_index ] ) ]

                decoded_message += param_name + "=" + str( value ) + "&"

                # Iterate the byte_index
                byte_index += 1

            elif param_values == "int-param":
                print( "Decoding int value" )

                try:
                    # Retreive the number of bytes dedicated to this integer
                    integer_length = int( parameter[ "length" ] )
                    print( integer_length )

                    # Retreive a sub array of the bytes dedicated to this parameter
                    integer_sub_array = byte_array[ byte_index:( byte_index + integer_length ) ]

                    print( integer_sub_array )

                    # Convert the array of bytes into an integers\
                    value = int.from_bytes( integer_sub_array, byteorder='big', signed=False)

                    print( value )

                    decoded_message += param_name + "=" + str( value ) + "&"

                    # Iterate the byte_index
                    byte_index += integer_length

                except IndexError as e :
                    # Catch the index error
                    print( type(e) )
                    print( "Byte missing for int-param" )
                    raise

            elif param_values == "float-param":
                print( "Decoding float value" )

                try:
                    # Retreive a sub array of the bytes dedicated to this parameter
                    float_sub_array = byte_array[ byte_index:( byte_index + FLOAT_PARAM_LENGTH ) ]
                    float_sub_array.reverse()

                    print( float_sub_array )

                    # Convert the array of bytes into a floating point number
                    value = struct.unpack( 'f', bytes( float_sub_array ) )[0]

                    print( value )

                    decoded_message += param_name + "=" + str( value ) + "&"

                    # Iterate the byte_index
                    byte_index += FLOAT_PARAM_LENGTH

                except IndexError as e :
                    # Catch the index error
                    print( type(e) )
                    print( "Byte missing for float-param" )
                    raise

            elif param_values == "double-param":
                print( "Decoding double value" )

                try:
                    # Retreive a sub array of the bytes dedicated to this parameter
                    double_sub_array = byte_array[ byte_index:( byte_index + DOUBLE_PARAM_LENGTH ) ]
                    double_sub_array.reverse()

                    print( double_sub_array )

                    # Convert the array of bytes into a floating point number
                    value = struct.unpack( 'd', bytes( double_sub_array ) )[0]

                    print( value )

                    decoded_message += param_name + "=" + str( value ) + "&"

                    # Iterate the byte_index
                    byte_index += DOUBLE_PARAM_LENGTH

                except IndexError as e :
                    # Catch the index error
                    print( type(e) )
                    print( "Byte missing for double-param" )
                    raise

        # Trim trailing "&"
        decoded_message = decoded_message[:-1]

        return decoded_message


def forward_message( message ):
    ''' Stub function that forwards the decoded message to its destination
        based on the URL and api name found in the decoding table. Currently,
        just prints out the resulting URL. '''
    print( "forward_message ran" )
    print( message )



def receive_message( socket ):
    ''' Receives a message from the LoRaMessenger library through the given socket.
        Reads the 4 byte header of the message to know how many bytes to expect. '''
    raw_message_length = receive_all( socket, 4 )

    if not raw_message_length:
        return None
    message_length = struct.unpack('>I', raw_message_length)[0]

    return receive_all( socket, message_length )


def receive_all( socket, n ):
    ''' Waits to receive all n bytes from the given sockets '''
    data = bytearray()
    while len(data) < n:
        packet = socket.recv( n - len(data) )
        if not packet:
            return None
        data.extend( packet )
    return data


def count_received_fragments(message):
    ''' Counts the number of fragments in a given message '''
    return len(message) // 13 + (len(message) % 13 > 0)


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



if __name__ == "__main__":
    sys.exit(main())
