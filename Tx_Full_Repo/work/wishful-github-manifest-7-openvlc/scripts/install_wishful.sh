#!/bin/bash

echo "Install required libraries ..."
sudo apt-get install wget git python python-virtualenv python-dev python3-dev python3-pip

echo "Create virtual environment ..."
virtualenv -p /usr/bin/python3 ./dev

echo "Activate virtualenv ..."
source ./dev/bin/activate

echo "Pip install wishful ..."
pip3 install -U -r ./.repo/manifests/requirements.txt