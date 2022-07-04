#!/bin/sh
apk add --no-cache bash python3 py3-pip
pip3 install hvac
set -a 
ENV=.env
source $ENV
set +a
python3 s3.py

