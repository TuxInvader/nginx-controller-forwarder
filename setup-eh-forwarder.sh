#!/bin/bash

FWDHOME=$(pwd)

sudo apt-get install -y python3-venv
python3 -m venv ${FWDHOME}/venv

source ${FWDHOME}/venv/bin/activate
pip install requests azure-eventhub 
pip install azure-eventhub-checkpointstoreblob

