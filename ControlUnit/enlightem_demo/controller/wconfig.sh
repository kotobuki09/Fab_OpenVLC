#!/bin/bash

FREQUENCY=`iwconfig | grep -o "Frequency:.*GHz" | sed -e "s/[^0-9.]//g"`
SSID_MODE=`iwconfig | grep -o "Mode:.*" | sed -e "s/\s.*//g" | sed -e "s/.*://g"`
LINK_QUALITY=`iwconfig | grep -o "Link Quality=[0-9]*/[0-9]*" | sed -e "s/.*=//g"`
ACCESS_POINT=`iwconfig | grep -o "Access Point:.*"  | grep -E -o "([0-9A-F]{2}:){5}[0-9A-F]{2}"`

SCAN_OUTPUT=`iwlist wlan0 scan`
CHANNEL=`echo $SCAN_OUTPUT | grep -E -o "($ACCESS_POINT\sChannel:[0-9]+)" | grep -E -o "(Channel).*" | grep -E -o "[0-9]+"`

echo "Frequency characteristic : $FREQUENCY Ghz"
echo "Channel                  : $CHANNEL"
echo "Device mode              : $SSID_MODE"
echo "Link quality             : $LINK_QUALITY"

