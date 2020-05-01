import json
import struct
import sys
sys.path.append("../")
import proxyServer


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
    encoding_outputs = json.load(file)

    index = 0

    # Iterate through the inputs
    for input in inputs:

        # Decode the message
        # decoded_message = handle_message( encoding_outputs[ index ], input["decoding"] )

        # Don't need to strip the metadata since we didn't run forwardMessage in RoundTripTest.kt
        byte_array =  list( encoding_outputs[ index ] )
        print( byte_array )

        # Retrieve the app and api bytes
        ( app_name_byte, api_name_byte ) = proxyServer.get_app_and_api( byte_array )

        # Read the appropriate encoding table based upon the app/api combo
        ( app_name, api_name, params_table ) = proxyServer.read_decoding_table( input["decoding"], app_name_byte, api_name_byte )

        # Decode the message
        decoded_message = proxyServer.decode_message( app_name, api_name, params_table, byte_array )

        # Compare the result to the original input
        print(f"Results of input #{index}\n")
        print(f"The resulting URL: {decoded_message}\n")

        appName = input["app"]
        apiName = input["api"]

        assert decoded_message.split('/')[0] == appName, f"The app names did not match. Expected {appName} but got {decoded_message.split('/')[0]}\n"

        decoded_message = decoded_message[decoded_message.find('/') + 1:]

        assert decoded_message.split('?')[0] == apiName, f"The api names did not match. Expected {apiName} but got {decoded_message.split('?')[0]}\n"

        decoded_message = decoded_message[decoded_message.find('?') + 1:]

        for parameter in input["params"]:

            if( decoded_message.find('&') != -1 ):
                result = decoded_message[decoded_message.find('=') + 1:decoded_message.find('&')]
            else:
                result = decoded_message[decoded_message.find('=') + 1:]

            assert str(result) == str(parameter), f"The values for param {decoded_message.split('=')[0]} did not match. Expected {parameter} but got {result}\n"

            decoded_message = decoded_message[decoded_message.find('&') + 1:]

        index += 1



if __name__ == "__main__":
    sys.exit(main())
