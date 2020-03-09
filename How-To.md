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

# Encoding-Files




# Decoding-Files

