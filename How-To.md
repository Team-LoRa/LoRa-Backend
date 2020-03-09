# Using the LoRaMessenge Configuration Service 

Table of contents:

[How to Format an Input File](#Input-Files)  

[How an Encoding File Should Look](#Encoding-Files)  

[How a Decoding File Should Look](#Decoding-Files)  


# Input-Files  

Input files must be in JSON format!  

Simply make the outter most keys in your JSON file the names of the apps you wish
to use with LoRaMessenger.  
Once you've named your Apps, their contents should be keyed as follows:  
- url : The address you wish to access. This should correspond with the app you're using
- api : each api should have its own key and it should have the following contents  
    * Parameter-name : this should be paired with a list with the following constraints  
    If the parameter accepts an arbitrary length int or double, specify which type at
    list index 0 and the max length of the parameter in index 1.  
    If the parameter only accepts specific values, simply place all the values in a list

Here is an example input-json file (this can also be found in the examples folder)
``` JSON
{
    "TempControl" : {
        "url" : "TempControl.com",
        "tempUp" : { "increaseAmount" : [ "int-param", "2" ], "room" : [ "Living Room", "Dining Room", "Kitchen", "Bedroom", "Garage"] },
        "tempDown" : { "decreaseAmount" : [ "int-param", "2" ], "room" : [ "Living Room", "Dining Room", "Kitchen", "Bedroom", "Garage"] }
    },
    "LightControl" : {
        "url" : "LightControl.com",
        "on" : { "intensity" : [ "int-param", "2" ], "room" : [ "Living Room", "Dining Room", "Kitchen", "Bedroom", "Garage"] },
        "off" : { "room" : [ "Living Room", "Dining Room", "Kitchen", "Bedroom", "Garage"] }
    }
}
```

# Encoding-Files
If everything went well, the encoding file should look like this:

``` JSON
{

  "TempControl" : {
    "byte_code" : "1",

    "tempUp" : {
      "byte_code" : "1",
      "params" : [
        {
          "name" : "increaseAmount",
          "values" : "int-param",
          "length" : "2"
        },
        {
          "name" : "room",
          "values" : {
            "Living Room" : "1",
            "Dining Room" : "2",
            "Kitchen" : "3",
            "Bedroom" : "4",
            "Garage" : "5"
          }
        }
      ]
    },

    "tempDown" : {
      "byte_code" : "2",
      "params" : [
        {
          "name" : "increaseAmount",
          "values" : "int-param",
          "length" : "2"
        },
        {
          "name" : "room",
          "values" : {
            "Living Room" : "1",
            "Dining Room" : "2",
            "Kitchen" : "3",
            "Bedroom" : "4",
            "Garage" : "5"
          }
        }
      ]
    }
  },

  "LightControl" : {
    "byte_code" : "2",

    "on" : {
      "byte_code" : "1",
      "params" : [
        {
          "name" : "intensity",
          "values" : "int-param",
          "length" : "2"
        },
        {
          "name" : "room",
          "values" : {
            "Living Room" : "1",
            "Dining Room" : "2",
            "Kitchen" : "3",
            "Bedroom" : "4",
            "Garage" : "5"
          }
        }
      ]
    },

    "off" : {
      "byte_code" : "2",
      "params" : {
        "name" : "room",
        "values" : {
          "Living Room" : "1",
          "Dining Room" : "2",
          "Kitchen" : "3",
          "Bedroom" : "4",
          "Garage" : "5"
        }
      }
    }
  }

}
```
This file should be placed in the Android assests folder


# Decoding-Files
If all went well then the decoding file should look like this:

``` JSON
{

  "1" : {
    "url" : "TempControl.com",

    "1" : {
      "name" : "tempUp",
      "params" : [
        {
          "name" : "increaseAmount",
          "values" : "int-param",
          "length" : "2"
        },
        {
          "name" : "room",
          "values" : {
            "1" : "Living Room",
            "2" : "Dining Room",
            "3" : "Kitchen",
            "4" : "Bedroom",
            "5" : "Garage"
          }
        }
      ]
    },

    "2" : {
      "name" : "tempDown",
      "params" : [
        {
          "name" : "increaseAmount",
          "values" : "int-param",
          "length" : "2"
        },
        {
          "name" : "room",
          "values" : {
            "1" : "Living Room",
            "2" : "Dining Room",
            "3" : "Kitchen",
            "4" : "Bedroom",
            "5" : "Garage"
          }
        }
      ]
    }

  },

  "2" : {
    "url" : "LightControl.com",

    "1" : {
      "name" : "on",
      "params" : [
        {
          "name" : "intensity",
          "values" : "int-param"
        },
        {
          "name" : "room",
          "values" : {
            "1" : "Living Room",
            "2" : "Dining Room",
            "3" : "Kitchen",
            "4" : "Bedroom",
            "5" : "Garage"
          }
        }
      ]
    },

    "2" : {
      "name" : "off",
      "params" : {
        "name" : "room",
        "values" : {
          "1" : "Living Room",
          "2" : "Dining Room",
          "3" : "Kitchen",
          "4" : "Bedroom",
          "5" : "Garage"
        }
      }
    }

  }

}
```
