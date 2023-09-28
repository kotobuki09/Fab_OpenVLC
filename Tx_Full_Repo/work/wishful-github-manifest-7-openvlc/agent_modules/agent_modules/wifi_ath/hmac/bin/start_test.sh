#!/bin/bash

echo "Standalone MAC test ... "

sudo ./64bit/x86_64/hybrid_tdma_csmaac -d 0 -i wifi0 -f 20000 -n 10
