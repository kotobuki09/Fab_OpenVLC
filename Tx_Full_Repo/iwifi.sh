#!/bin/bash

t1=$(iperf -c 10.0.0.16 -u -p 10002 -t 1 -r -y C|cut -d',' -f10)
print(t1)
