import json
import sys
import os

def main(fileName):
    """ load json file specified by the 1st cli argument.
    Gets loaded as a standard python dict """
    param_dict = {}
    api_dict = {}
    app_dict = {}
    param_counter = 1
    app_counter = 1
    api_counter = 1
    with open(fileName) as devJSON:
        dictJSON = json.load(devJSON)
        # find the message types the dev submitted
        #testList = keyListBuilder(dictJSON)
        for (app_name, api_method_list) in dictJSON.items():
            for (api_method, param_list) in api_method_list.items():
                print(param_list)
                for param in param_list:
                    param_dict[param_counter] = param
                    param_counter += 1
                api_dict[api_counter] = api_method
                api_counter += 1
            app_dict[app_counter] = app_name
            app_counter += 1
        '''print(app_dict)
        print(api_dict)
        print(param_dict) '''
       
def encode(name, upper_dict, count = 1):
    pass


if __name__ == "__main__":
    main(sys.argv[1])