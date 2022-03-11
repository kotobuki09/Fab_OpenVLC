#! /usr/bin/env python3

import os
import os.path
import datetime
import re
import fabric.api as fab
import fabric.utils

from fabric.api import env

@fab.task
def STA_TX():
    #env.hosts={'domenico@10.8.9.13:22'}
    #env.passwords = {'domenico@10.8.9.13:22': 'labtti2015'}
    env.hosts={'domenico@10.8.9.18:22'}
    env.passwords = {'domenico@10.8.9.18:22': 'ttilab'}

@fab.task
def MONITOR():
    env.hosts={'admin@10.8.8.123:22'}
    env.passwords = {'admin@10.8.8.123:22': 'ttilabttilab'}

@fab.task
def AP():
    #env.hosts={'pi@10.8.8.210:22'}
    #env.passwords = {'pi@10.8.8.210:22': 'password'}
    env.hosts={'pi@10.8.8.211:22'}
    env.passwords = {'pi@10.8.8.210:22': 'raspberry'}

@fab.task
def setup_sta_tx():
    fab.sudo("systemctl stop NetworkManager.service")
    fab.sudo("systemctl disable NetworkManager.service")
    fab.run("iw dev wlan0 link")
    fab.sudo("ifconfig wlan0 up")
    fab.sudo("iw dev wlan0 scan | grep DFL")
    fab.sudo("iw dev wlan0 disconnect")
    fab.sudo("iw dev wlan0 connect RASP-DFL-5G")
    fab.sudo("dhclient wlan0")
    fab.run("iw dev wlan0 link")



@fab.task
def setup_ap():
    fab.sudo("killall -9 hostapd")
    fab.sudo("hostapd -i wlan0 /home/pi/merc-experiment-setup/hostapdac2.conf -B")
    fab.sudo("ifconfig wlan0 192.168.1.1")


##./utils/makecsiparams/makecsiparams -c 36/80 -C 0xf -N 0x1 -b 0x88 -m A0:C5:89:56:9D:A2 #NUC1
monitor_config_str="KuABHwGIAQCgxYlWnaIAAAAAAAAAAAAAAAAAAAAAAAAAAA=="

##./utils/makecsiparams/makecsiparams -c 36/20 -C 0xf -N 0x1 -m A0:C5:89:56:9D:A2
#monitor_config_str="JNABHwAAAQCgxYlWnaIAAAAAAAAAAAAAAAAAAAAAAAAAAA=="


##./utils/makecsiparams/makecsiparams -c 36/80 -C 0xf -N 0x1 -m A0:C5:89:56:9D:A2
#monitor_config_str="KuABHwAAAQCgxYlWnaIAAAAAAAAAAAAAAAAAAAAAAAAAAA=="

##./utils/makecsiparams/makecsiparams -c 40/80 -C 0xf -N 0x1 -m A0:C5:89:56:9D:A2
#monitor_config_str="KuEBHwAAAQCgxYlWnaIAAAAAAAAAAAAAAAAAAAAAAAAAAA=="

##./utils/makecsiparams/makecsiparams -c 40/80 -C 0xf -N 0x1 -b 0x80 -m A0:C5:89:56:9D:A2
#monitor_config_str="KuEBHwGAAQCgxYlWnaIAAAAAAAAAAAAAAAAAAAAAAAAAAA=="

@fab.task
def setup_monitor():
    print("\033[1m"+"WARNING: RUN THIS COMMAND ONLY FIRST TIME AT MONITOR BOOT, OTHER ACTIVATIONS WILL CAUSE A PANIC AND REBOOT"+"\033[0m")
    input_choice = raw_input("continue?[y/N]")
    #input_choice='n'
    if input_choice=='y':
        fab.run("wl -i eth6 down")
        fab.run("wl -i eth5 down")
        fab.run("/sbin/rmmod dhd; /sbin/insmod /jffs/dhd.ko")
        fab.run("wl -i eth6 up")
        fab.run("ifconfig eth6 up")
        with fab.cd('/jffs/'):
            fab.run("./nexutil -Ieth6 -s500 -b -l34 -v"+monitor_config_str)
        fab.run("wl -i eth6 monitor 1")
    else:
        print("skipped dhd module load, do iface up/down...")
        fab.run("wl -i eth6 down")
        fab.run("wl -i eth5 down;")
        fab.run("wl -i eth6 up")
        fab.run("ifconfig eth6 up")
        with fab.cd('/jffs/'):
            fab.run("./nexutil -Ieth6 -s500 -b -l34 -v"+monitor_config_str)
        fab.run("wl -i eth6 monitor 1")


@fab.task
def monitor_pcap_acquire(pcap_filename,duration=120):
    pcap_array=pcap_filename.rsplit('/', 1)
    from fabric.contrib import files
    fab.run('mkdir -p '+pcap_array[0])
    tcpdump_cmd="nohup tcpdump -i eth6 dst port 5500 -s0 -w {} &> /dev/null & ".format(pcap_filename)
    fab.run(tcpdump_cmd,pty=False)

@fab.task
def stop_monitor():
    fab.run("killall -9 tcpdump", pty=False)


@fab.task
def start_iperf_server():
    command = 'nohup %s &> /dev/null &' % "iperf -s -u -i1 -p 12345"
    fab.run(command, pty=False)
    #command = "iperf -s -u -i1 -p 12345"
    #fab.run(command)

@fab.task
def stop_iperf():
    fab.run("killall -9 iperf")

@fab.task
def start_iperf_client(duration=120):
    #set bitrate
    #fab.sudo("iw dev wlan0 set bitrates vht-mcs-5 1:4")
    #start iperf
    command = "nohup iperf -c 10.3.141.1 -p 12345 -u -t60 -i 1 -b 2M -t {} &> /dev/null &".format(duration)
    fab.run(command, pty=False)
@fab.task
def start_raw_ip_sender(samptime=5e-3,duration=10):
    fab.sudo("iw dev wlan0 set bitrates vht-mcs-5 1:4")
    fab.sudo("nohup python3 ~/sendRawFrame.py -t {} -d {}&> /dev/null &".format(samptime,duration))
@fab.task
def get_pcap(filename):
    #fab.get("/mnt/sda/{}".format(filename),"/media/fabrizio/data/ownCloudTTI/work/UNIPA/NEXMON_CSI_2.0/csi-pcap/lab/")
    remote_filename="/mnt/sda/{}".format(filename)
    print(remote_filename)
    fab.get(remote_filename,"~/")

@fab.task
def getTxInfo():
    fab.run("iw dev wlan0 link")
