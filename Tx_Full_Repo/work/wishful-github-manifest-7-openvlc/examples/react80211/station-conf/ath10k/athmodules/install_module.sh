#!/bin/bash

rmmod ath10k_pci
rmmod ath10k_core
rmmod ath
rmmod mac80211
rmmod cfg80211
rmmod compat
insmod ./compat.ko 
insmod ./cfg80211.ko 
insmod ./mac80211.ko 
insmod ./ath.ko 
insmod ./ath10k_core.ko 
insmod ./ath10k_pci.ko

