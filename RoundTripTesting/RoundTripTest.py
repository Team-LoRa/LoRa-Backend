import json
import struct
import sys



# The number of bytes allocated to an arbitrary float parameter
FLOAT_PARAM_LENGTH = 4
# The number of bytes allocated to an arbitrary double parameter
DOUBLE_PARAM_LENGTH = 8



def main():
    # Read the input file
    file = open("round_trip_input.json", 'r')
    inputs = json.load(file)

    # Read the encoding output file
    file = open("encoding_output.json", 'r')
    encodingOutputs = json.load(file)

    index = 0

    # Iterate through the inputs
    for input in inputs:

        # Decode the message
        decodedMessage = handle_message( encodingOutputs[ index ], input["decoding"] )

        # Compare the result to the original input
        print(f"Results of input #{index}\n")
        print(f"The resulting URL: {decodedMessage}\n")

        appName = input["app"]
        apiName = input["api"]

        assert decodedMessage.split('/')[0] == appName, f"The app names did not match. Expected {appName} but got {decodedMessage.split('/')[0]}\n"

        decodedMessage = decodedMessage[decodedMessage.find('/') + 1:]

        assert decodedMessage.split('?')[0] == apiName, f"The api names did not match. Expected {apiName} but got {decodedMessage.split('?')[0]}\n"

        decodedMessage = decodedMessage[decodedMessage.find('?') + 1:]

        for parameter in input["params"]:

            if( decodedMessage.find('&') != -1 ):
                result = decodedMessage[decodedMessage.find('=') + 1:decodedMessage.find('&')]
            else:
                result = decodedMessage[decodedMessage.find('=') + 1:]

            assert str(result) == str(parameter), f"The values for param {decodedMessage.split('=')[0]} did not match. Expected {parameter} but got {result}\n"

            decodedMessage = decodedMessage[decodedMessage.find('&') + 1:]

        index += 1




def handle_message( message, filename):
    ''' Decodes the given message based on the information found in
        decoding_table.json, then forwards the message to its intended
        destination. '''
    print( "handle message began" )
    # Convert the string of bytes into an array of bytes
    byte_array = list( message )

    # Retrieve the app and api bytes
    ( app_name_byte, api_name_byte ) =  get_app_and_api(byte_array)

    # Read the appropriate encoding table based upon the app/api combo
    ( app_name, api_name, params_table ) = read_decoding_table(app_name_byte, api_name_byte, filename)

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

                try:
                    # Retreive the number of bytes dedicated to this integer
                    integer_length = int( parameter[ "length" ] )

                    # Retreive a sub array of the bytes dedicated to this parameter
                    integer_sub_array = byte_array[ byte_index:( byte_index + integer_length ) ]

                    print( bytes( integer_sub_array ) )

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

                try:
                    # Retreive a sub array of the bytes dedicated to this parameter
                    float_sub_array = byte_array[ byte_index:( byte_index + FLOAT_PARAM_LENGTH ) ]
                    float_sub_array.reverse()

                    print( bytes( float_sub_array ) )

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

                try:
                    # Retreive a sub array of the bytes dedicated to this parameter
                    double_sub_array = byte_array[ byte_index:( byte_index + DOUBLE_PARAM_LENGTH ) ]
                    double_sub_array.reverse()

                    print( bytes( double_sub_array ) )

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

    # Return the message so it can be compared to the original input
    return decoded_message


def read_decoding_table( app_byte, api_byte, filename):
    ''' Reads the file decoding_table.json and parses it to determine the
        name of the app that sent the message, the name of the api the
        message is using, and a list of parameters to expect with the
        message. '''
    print( "read_decoding_table ran; app: " + str(app_byte) + " api: " + str(api_byte) )

    try:
        # Open the encoding table file and convert it into a dictionary
        file = open(filename, 'r')
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

        return( app_table[ "url" ], api_table[ "name" ], api_table[ "params" ] )

    except KeyError as e :
        # Catch key error
        print( type(e) )
        print( "Decoding table missing information" )
        raise


def forward_message( message):
    ''' Stub function that forwards the decoded message to its destination
        based on the URL and api name found in the decoding table. Currently,
        just prints out the resulting URL. '''
    print( "forward_message ran" )
    print( message )


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
    print( total_number_fragments )
    print( count_received_fragments(message) )
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
