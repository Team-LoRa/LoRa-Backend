import json
import sys
import os

def main(fileName):
    """ load json file specified by the 1st cli argument.
    Gets loaded as a standard python dict """
    with open(fileName) as devJSON:
        dictJSON = json.load(devJSON)
        # find the message types the dev submitted
        #testList = keyListBuilder(dictJSON)
        app_counter = 1
        app_dict = {}
        for (app_name, api_method_list) in dictJSON.items():
            temp_api = {}
            api_counter = 1
            for (api_method, param_list) in api_method_list.items():
                temp_params = {}
                param_counter = 1
                for param in param_list:
                    temp_params[param_counter] = param
                    param_counter += 1
                temp_api[api_counter] = temp_params
                api_counter += 1
            app_dict[app_counter] = temp_api
            app_counter += 1
    with open("output.json", 'w') as output:
        json.dump(app_dict, output)  

if __name__ == "__main__":
    main(sys.argv[1])