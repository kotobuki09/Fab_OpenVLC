import fabric.api as fab
import fabric.utils
from fabric.api import run, env, execute, roles
from fabric.context_managers import cd
import time

command = 'nohup %s &> /dev/null &' % "iperf -c 192.168.0.2 -u -b 1M -l 800 -p 10001 -t 10"

#env.hosts={'debian@10.8.10.5'}
#env.roledefs = { 'vlc1': ['debian@10.8.10.5'], 'vlc2': ['debian@10.8.10.8'] }
#env.passwords = { 'debian@10.8.10.5:22':'temppwd', 'debian@10.8.10.8:22':'temppwd' }

#nice workaround solution to embed the host access parameters as a fabric task
@fab.task
def vlc1():
    env.hosts={'debian@10.8.10.5'}
    env.passwords = {'debian@10.8.10.5:22':'temppwd'}

@fab.task
def vlc2():
    env.hosts={'debian@10.8.10.8'}
    env.passwords = {'debian@10.8.10.8:22':'temppwd'}

@fab.task
def getRSSI():
    output=fab.sudo("python3 getRSSI.py")
    return output

@fab.task
def start_iperf_client(type=""):
    #fab.run("killall -9 iperf")
    if type=="vlc":
        command = 'nohup %s &> /dev/null &' % "iperf -c 192.168.0.2 -u -b 1M -l 800 -p 10001 -t 10"
    elif type=="wifi":
        command = 'nohup %s &> /dev/null &' % "iperf -c 192.168.12.26 -u -b 1M -l 800 -p 10002 -t 100000"
    else:
        command = 'nohup %s &> /dev/null &' % "iperf -c 192.168.10.2 -u -b 1000M -l 800 -p 10003 -t 100000"
    fab.run(command, pty=False)

@fab.task
def stop_iperf():
    fab.run("killall iperf")

@fab.task
def start_iperf_server(type=""):
    #start iperf
    #fab.sudo("killall -q iperf",pty=True)
    if type=="vlc":
        #rx_host="192.168.0.2"
        command = "iperf -u -l 800 -s -i3 -B 192.168.0.2 -p 10001"
    elif type=="wifi":
        #rx_host="192.168.12.26"
        command = "iperf -u -l 800 -s -i3 -B 192.168.12.26 -p 10002"
    else:
        rx_host="192.168.10.2"
        command = "iperf -u -l 800 -s -i3 -B 192.168.10.2 -p 10003"

    command = "iperf -u -l 800 -s -i3 -B {} -p 10003".format(rx_host)
    fab.run(command, pty=False)

@fab.task
def setup_wifi_ap():
    fab.sudo("service dnsmasq stop")
    fab.sudo("create_ap -c 6 -n wlan0 MyAccessPoint 12345678")

@fab.task
def setup_wifi_sta():
    fab.sudo("connmanctl scan wifi")
    fab.sudo("connmanctl connect wifi_74da38e6ba57_4d79416363657373506f696e74_managed_psk")

@fab.task
def setup_vlc_tx():
    with cd('/home/debian/OpenVLC/Latest_Version/'):
        fab.sudo("./tx.sh")


@fab.task
def setup_vlc_rx():
    with cd('/home/debian/OpenVLC/Latest_Version/'):
        fab.sudo("./rx.sh")

@fab.task
def v_inf(type="tx"):
    if type=="tx":
        fab.sudo = ("ip link add eth10 type dummy")
        fab.sudo = ("ifconfig eth10 hw ether 00:22:22:ff:ff:ff")
        fab.sudo = ("ip addr add 192.168.10.1/24 brd + dev eth10 label eth10:0")
    else:
        fab.sudo = ("sudo ip link add eth10 type dummy")
        fab.sudo = ("sudo ifconfig eth10 hw ether 00:22:22:ff:ff:f0")
        fab.sudo = ("sudo ip addr add 192.168.10.2/24 brd + dev eth10 label eth10:0")

#@roles('vlc1')
@fab.task
def wifi_link():
    #fab.sudo = ("route add -net 192.168.10.0 gw 192.168.12.1 netmask 255.255.255.0 dev ap0")
    #fab.sudo = ("route del -net 192.168.10.0 gw 192.168.0.1 netmask 255.255.255.0 dev vlc0")
    #fab.run = ("route del -net 192.168.10.0 gw 192.168.0.1 netmask 255.255.255.0 dev vlc0 && route add -net 192.168.10.0 gw 192.168.12.1 netmask 255.255.255.0 dev ap0")
    with cd('/home/debian/OpenVLC/Latest_Version/'):
        fab.sudo("./wifi_link.sh")

#@roles('vlc1')
@fab.task
def vlc_link():
    #fab.sudo = ("route add -net 192.168.10.0 gw 192.168.0.1 netmask 255.255.255.0 dev vlc0")
    #fab.sudo = ("route del -net 192.168.10.0 gw 192.168.12.1 netmask 255.255.255.0 dev ap0")
    #fab.sudo = ("route del -net 192.168.10.0 gw 192.168.12.1 netmask 255.255.255.0 dev ap0 && route add -net 192.168.10.0 gw 192.168.0.1 netmask 255.255.255.0 dev vlc0")
    with cd('/home/debian/OpenVLC/Latest_Version/'):
        fab.sudo("./vlc_link.sh")

#The stream will make a jump to different network after 10 seconds
@fab.task
def schedule_controller():
    while True: 
        execute('vlc_link')
        time.sleep(5)
        execute('wifi_link')
        time.sleep(5)

@fab.task
def iperf1()
     execute(vlc1)
     fab.sudo = ("iperf -c 192.168.0.2 -u -b 1M -l 800 -p 10001 -t 20")

@fab.task
def iperf2():
     execute(vlc2)
     fab.sudo= ("iperf -u -l 800 -s -i3 -B 192.168.0.2 -p 10001")

#Intelligent Control
@fab.task
def icontrol(capture=True):
    T=1
    Twatchdog=0.5
    execute(vlc1)
    execute(vlc_link)
    current_state="VLC"
    time.sleep(T)

    while 1:
        #Watchdog for VLC
        if current_state=="WIFI":
            #Check the VLC connection
            execute(vlc1)
            execute(iperf1)
            execute(vlc2)
            execute(iperf2)
            output = execute(getRSSI)
            output=output[list(env.hosts)[0]].split(" ")
            print(output)
            output = [int(i) for i in output]
            print("Checking the RSSI value in VLC channel: "+str(output))
            #print("CURRENT STATE={}".format(current_state))
            if output[0]>1090:
                print("Switching to VLC channel 1 \n")
                execute(vlc1)
                execute(vlc_link)
                current_state="VLC"
        else: 
        #RX
            execute(vlc2)
            output = execute(getRSSI)
            output=output[list(env.hosts)[0]].split(" ")
            print(output)
	    output = [int(i) for i in output]
            print("Checking the RSSI value in VLC channel: "+str(output))
            #print("CURRENT STATE={}".format(current_state))

            if output[0]<1090 and current_state=="VLC":
                print("Switching to WiFi channel \n")
                execute(vlc1)
                execute(wifi_link)
                current_state="WIFI"
            else:
            #if current_state=="WIFI":
                print("Switching to VLC channel 2 \n")
                execute(vlc1)
                execute(vlc_link)
                current_state="VLC"
        time.sleep(1)
