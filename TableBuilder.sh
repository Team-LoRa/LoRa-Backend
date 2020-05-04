#!/bin/bash

read -p 'Please enter the JSON file name: ' jsonfile

python ./decoding.py $jsonfile
python ./encoding.py $jsonfile
