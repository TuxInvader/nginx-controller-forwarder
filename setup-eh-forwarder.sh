#!/bin/bash

FWDHOME=$(pwd)

sudo apt-get install -y python3-venv
python3 -m venv ${FWDHOME}/venv

source ${FWDHOME}/venv/bin/activate
pip install requests azure-eventhub 
pip install azure-eventhub-checkpointstoreblob

read -p "Please enter the EventHub Connection String: " evh_c
read -p "Please enter the EventHub Name: " evh_n
read -p "Please enter your NGINX Controller user: " ctl_u
read -p "Please enter your NGINX Controller password: " ctl_p

cat systemd/forwarder.service | sed -re "s#FORWARD_PYTHON#${FWDHOME}/venv/bin/python ${FWDHOME}/eventhub_forwarder.py#" | \
    sed -re "s#FORWARD_ENV#Environment=EVENT_HUB_CONN_STR=${evh_c} EVENT_HUB_NAME=${evh_n} CONTROLLER_USER=${ctl_u} CONTROLLER_PASS=${ctl_p}#" | \
    sed -re "s#FORWARD_DESC#Azure EventHubs Forwarder#" | sudo tee /lib/systemd/system/evh-forwarder.service


