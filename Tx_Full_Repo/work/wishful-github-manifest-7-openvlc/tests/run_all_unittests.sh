#!/bin/bash

echo "Testing local controller ..."
cd ./local/linux/ ; ./run_unittest_on_linux.sh ; cd ../..

sleep 1

if which mn >/dev/null; then
    echo "Testing local controller in mininet ..."
    cd ./local/mininet/ ; ./run_unittest_on_linux_wifi.sh ; cd ../..

    sleep 1

    echo "Testing global controller in mininet ..."
    cd ./global/mininet/ ; ./run_unittest_on_linux_wifi.sh ; cd ../..
else
    echo "no mininet installed; skip test"
fi



