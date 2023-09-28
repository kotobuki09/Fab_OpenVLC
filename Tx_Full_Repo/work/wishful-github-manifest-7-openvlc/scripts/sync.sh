#!/bin/bash
echo "repo sync"
python2 ./repo sync
echo "Switch to master ..."
python2 ./repo start master --all