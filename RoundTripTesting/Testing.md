# Running Round-trip tests on the LoRaMessenger framework

Table of contents:

[Environment](#Environemtn)  

[Adding Testcases](#Adding Testcases)  

[Running the Tests](#Running the Tests)

This folder contains our slightly hacky framework for performing round-trip tests
on the LoRaMessenger framework.The basic structure of these tests are:

  - Read round_trip_input.json to obtain the name of an encoding table,
    app name, api name, and a list of parameters.
  - Pass all this information to a LoRaMessenger object and have in encode the
    message
  - Save the resulting encoded message to encoding_output.json
  - Read encoding_output.json and round_trip_input.json to obtain the name of a
    decoding table, the encoded message, and original list of parameters.
  - Pass all this information to the handle_message subprocess of the proxy server
  - Compare the resulting decoded message to the original input and report any
    discrepancies

# Environment

One challenge with running these round-trip tests is that LoRaMessenger was built
to run on Android devices and getting its output from an emulator or physical
device would be cumbersome. Fortunately, Kotlin also has a command line compiler
that can run Kotlin on a local machine. This will require that you have the
Java Runtime Environment installed.

If you are on Ubuntu, Kotlin can be easily installed with:

```
sudo snap install --classic kotlin
```

For method on how to install Kotlin on other systems, please check out this
tutorial: https://kotlinlang.org/docs/tutorials/command-line.html

The RoundTripTest.kt file can be compiled with:

```
kotlinc RoundTripTest.kt -cp json.jar LoraNodeConnection.kt -include-runtime -d RoundTripTest.jar
```

The resulting RoundTripTest.jar file can be ran with:

```
java -cp RoundTripTest.jar:json.jar:LoraNodeConnection.kt RoundTripTestKt
```

These commands to compile and run RoundTripTest.kt are also automatically ran by
RunRoundTripTest.py for convenience.

# Adding Testcases

Two testcases are already included in round_trip_input.json. If you would like to
add additional test cases, simply append add hash objects to the list in the file.
These hashes should be of the form:

```
{
  "encoding" : path to encoding table,
  "decoding" : path to decoding table,
  "app" : app name,
  "api" : api name,
  "params" : comma seperated list of parameters
}
```

Keep in mind that for any test case, you will need to create and include the
appropriate encoding and decoding tables.

# Running the Tests

To run all the test simply run:

```
python3 RunRoundTripTest.py
```

If any errors are found, they will be reported in the terminal.
