# Using the LoRaMessenger Proxy Server

Table of contents:

[Warnings](#Warnings)  

[Setup and Quickstart](#Setup and Quickstart)  

[Networking](#Networking)  

[Format of Forward Messages](#Format of Forwarded Messages)

The LoRaMessenger proxy server is the backend half of the LoRaMessenger framework
It is intended to run on some light-weight computer like a RasberryPi or Amazon
Web Service EC2 and sit between a LoRa Gateway and the broader internet. The
proxy is responsible for rebuilding, decoding, and forwarding the messages sent
by the LoRaMessenger Android library.

# Warnings

- The proxy server does nothing to encrypt or otherwise secure the messages it
receives and forwards. As such, avoid using this framework to send any kind of
sensitive information.

- The proxy server is an extremely simple, dumb server. It wasn't tested with
a high load of incoming messages and likely won't handle such a situation
that well. As such, this framework might struggle or break under large network
loads.

# Setup and Quickstart

The proxy server was built with Python3 and relies on a number of
Python3 packages. The pip3 package manager which comes with Python3 should be
sufficient to install everything with

```
pip3 install [module]
```

The proxyServer.py executable must be in the same directory as the
decoding_table.json file produced by the configuration service.

You can start the proxy server with:

```
python3 proxyServer.py [port number]
```

If no port number is given, the proxy will default to using port 2080. Currently,
the proxy server waits indefinitely for messages until it is stopped with a
keyboard interrupt.

# Format of Forwarded Messages

This proxy server was made with the intention of supporting API calls to web
applications over a LoRaWAN network. With this in mind, the proxy server makes
certain assumptions about how to format messages it receives.



For example, for the following decoding table the proxy server will forward a
message with parameters [ 12.314, 13.564, 46, 2367, 85476, 1348493027 ] as

```
"OpenCellID.com/measure/add?lat=12.314&lon=13.564&mcc=46&mnc=2367&lac=85476&cellid=1348493027"
```

```
{

  "1" : {
    "url" : "OpenCellID.com",

    "1" : {
      "name" : "measure/add",
      "params" : [
        {
          "name" : "lat",
          "values" : "double-param"
        },
        {
          "name" : "lon",
          "values" : "double-param"
        },
        {
          "name" : "mcc",
          "values" : "int-param",
          "length" : "1"
        },
        {
          "name" : "mnc",
          "values" : "int-param",
          "length" : "2"
        },
        {
          "name" : "lac",
          "values" : "int-param",
          "length" : "3"
        },
        {
          "name" : "cellid",
          "values" : "int-param",
          "length" : "4"
        }
      ]
    }

  }

}
```

# Networking

Currently, The proxy server assumes that the LoRa Gateway will be communicating
to it over a traditional TCP/IP connection. If this isn't the case, you will
need to modify the proxy server to fit with your network architecture.

Implementing the proxy server an MQTT client which would receive messages
published by the LoRa Gateway was experimented with. That unfinished stub of the
proxy server is found in proxyServerMQTT.py.
