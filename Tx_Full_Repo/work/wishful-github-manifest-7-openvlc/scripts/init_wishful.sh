#!/bin/bash

echo "Install required libraries ..."
sudo apt-get install wget git python python-virtualenv python-dev python3-dev python3-pip

echo "Get repo ..."
wget https://storage.googleapis.com/git-repo-downloads/repo

chmod a+x ./repo

echo "Init repo ..."
python2 ./repo init -u ssh://git@gitlab.tubit.tu-berlin.de/wishful/wishful_manifests.git

echo "Repo sync ..."
python2 ./repo sync

echo "Switch to master ..."
python2 ./repo start master --all

echo "Check status of all repositories ..."
python2 ./repo status

echo "Create virtual environment ..."
virtualenv -p /usr/bin/python3 ./dev

echo "Activate virtualenv ..."
source ./dev/bin/activate

echo "Pip install wishful ..."
pip3 install -U -r ./.repo/manifests/requirements.txt