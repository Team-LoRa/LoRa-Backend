import json
import sys
import os

def main(fileName):
    """ load json file specified by the 1st cli argument.
    Gets loaded as a standard python dict """
    with open(fileName) as devJSON:
        dictJSON = json.load(devJSON)

        # Separate all app dicts and place them into a list in the same order
        appsList = separateApps(dictJSON)

        decoding_table = {}

        appCounter = 1
        for key in appsList:
            # get the app name
            upperKey = list(key)[0]
            # use the app name to retrieve the corresponding dict
            workingAppDict = key.get(upperKey)

            # jump over the url and get the corresponding apis
            apiKeys = list(workingAppDict)[1:]
            # get the url
            url = workingAppDict.get("url")
            apiCounter = 1
            tempAppDict = {"url" : url}

            # iterate over the apis an app has
            for api in apiKeys:
                workingApiDict = workingAppDict.get(api)
                tempParamList = []

                # iterate over the params an api has
                for param in workingApiDict:
                    tempParamDict = paramBuilder(workingApiDict, param)
                    tempParamList.append(tempParamDict)

                builtApiDict = {"name" : api, "params" : tempParamList}
                tempAppDict[apiCounter] = builtApiDict
                apiCounter += 1

            decoding_table[appCounter] = tempAppDict
            appCounter += 1

    with open("decoding_table.json", 'w') as output:
        json.dump(decoding_table, output)  


def separateApps(theDict):
    ''' separates the starting dictionary into multiple dictionaries then
    puts them into a list to be used '''
    retList = []
    for appName in theDict.keys():
        tempDict = { appName : theDict.get(appName) }
        retList.append(tempDict)
    return retList


def apiBuilder(apiDict):
    pass


def paramBuilder(paramDict, paramName):
    ''' builds a param dictionary.
    checks to see if a param takes an arbitrary value based on formatting.
    if the param accepts only specific values, it pairs them with their
    index + 1. '''
    retDict = {"name" : paramName}
    workingList = paramDict.get(paramName)

    if workingList[0].find("param") >= 0:
        retDict["values"] = workingList[0]
        retDict["length"] = workingList[1]

    else:
        valuesDict = {}
        for counter, value in enumerate(workingList):
            valuesDict[str(counter+1)] = value
        retDict["values"] = valuesDict

    return retDict


if __name__ == "__main__":
    main(sys.argv[1])