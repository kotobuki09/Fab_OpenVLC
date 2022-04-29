import fabric.api as fab
import fabric.utils
from fabric.api import run, env, execute, roles, settings, hide
from fabric.context_managers import cd
import time



#env.hosts={'debian@10.8.10.5'}
env.roledefs = { 'vlc1': ['debian@10.8.10.5'], 'vlc2': ['debian@10.8.10.8'] }
env.passwords = { 'debian@10.8.10.5:22':'temppwd', 'debian@10.8.10.8:22':'temppwd' }

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
def vlc3():
    env.hosts={'debian@10.8.10.6'}
    env.passwords = {'debian@10.8.10.6:22':'temppwd'}

@fab.task
def getRSSI():
    output=fab.sudo("python3 getRSSI.py")
    return output

@fab.task
def start_iperf_client(type=""):
    #fab.run("killall -9 iperf")
    if type=="vlc":
        command = 'nohup %s &> /dev/null &' % "iperf -c 192.168.0.2 -u -b 1M -l 800 -p 10001 -t 100000"
    elif type=="wifi":
        command = 'nohup %s &> /dev/null &' % "iperf -c 10.0.0.16 -u -b 1M -l 800 -p 10002 -t 100000"
    else:
        command = 'nohup %s &> /dev/null &' % "iperf -c 192.168.10.2 -u -b 1000M -l 800 -p 10003 -t 100000"
    fab.run(command, pty=False)

@fab.task
def stop_iperf():
    fab.sudo("killall iperf")

@fab.task
def start_iperf_server(type=""):
    #start iperf
    #fab.sudo("killall -q iperf",pty=True)
    if type=="vlc":
        rx_host="192.168.0.2"
        #command = "iperf -u -l 800 -s -i3 -B 192.168.0.2 -p 10001"
    elif type=="wifi":
        rx_host="192.168.12.26"
        #command = "iperf -u -l 800 -s -i3 -B 10.0.0.16 -p 10002"
    else:
        rx_host="192.168.10.2"
        command = "iperf -u -l 800 -s -i3 -B 192.168.10.2 -p 10003"

    command = "iperf -u -l 800 -s -i3 -B {} -p 10003".format(rx_host)
    fab.run(command, pty=False)

@fab.task
def setup_wifi_ap():
    #fab.sudo("service dnsmasq stop")
    #fab.sudo("create_ap -c 6 -n wlan0 MyAccessPoint 12345678")
    fab.sudo("killall wpa_supplicant") 
    fab.sudo("sudo hostapd -B /etc/hostapd/hostapd.conf")

@fab.task
def setup_wifi_sta():
    fab.sudo("connmanctl scan wifi")
    fab.sudo("connmanctl connect wifi_7c8bca088c00_6f70656e564c432d73736964_managed_none")

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
        start_time = time.time()
        execute('vlc_link')
        wifiToVLC_time = time.time() - start_time
        print("Wifi to VLC : " + str(wifiToVLC_time))
        
        time.sleep(10)
        
        start_time2 = time.time()
        execute('wifi_link')
        vlcToWifi_time = time.time() - start_time2
        print("VLC to WiFi : " + str(wifiToVLC_time))
        time.sleep(30)

@fab.task
def iperf1():
    #fab.sudo=("iperf -c 192.168.0.2 -u -b 1M -l 800 -p 10001 -t 100000")
    fab.sudo = ('nohup %s &> /dev/null &' % "iperf -c 192.168.0.2 -u -b 10M -l 800 -p 10003 -t 100000")

@fab.task
def iperf2():
    #fab.sudo=("iperf -u -l 800 -s -i3 -B 192.168.0.2 -p 10001")
    fab.sudo = ('iperf -u -l 800 -s -i3 -B 192.168.0.2 -p 10003')

@roles('vlc1')
@fab.task
def dumpUDP():
    #with cd('/home/debian/OpenVLC/Latest_Version/'):
    fab.sudo("python3 dumpUDP 192.168.0.2 55555 &")

@fab.task
def kill_dumpUDP():
    with settings( hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
        fab.sudo("ps aux | grep dumpUDP | grep -v grep | awk '{print $2}' | xargs kill")

@fab.task
def wchannel(capture=True):
    link_quality = int(fab.sudo('iwconfig wlan0 | grep -o "Link Quality=[0-9]*" | sed -e "s/.*=//g"'))
    signal_level = int(fab.sudo('iwconfig wlan0 | grep -o "Signal level=-[0-9]*" | sed -e "s/.*=//g"'))
    noise_level = int(fab.sudo('iwconfig wlan0 | grep -o "Noise level=[0-9]*" | sed -e "s/.*=//g"'))
    print("link quality = %d" %link_quality)
    print("signal_level = %d" %signal_level)
    print("noise_level = %d" %noise_level)
    if link_quality >= 90:
        print("Link quality channel: %d >=90 \n" %(link_quality))
    else:
        print("Link quality channel: %d <90 \n" %(link_quality))

@fab.task
def iwifi(capture=True):
    iwifi=fab.sudo("python3 iwifi.py")
    iwifi=iwifi.split()
    print(iwifi)
    print(type(iwifi))
    print("Bandwidth = %s, Jitter = %s, LossP = %s " %(iwifi[0], iwifi[1], iwifi[2]))

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
            execute(vlc1)
            execute(dumpUDP)
            #execute(vlc_link)
            #current_state="VLC"
            time.sleep(Twatchdog)
        #RX
        execute(vlc2)
        output = execute(getRSSI)
        output=output[list(env.hosts)[0]].split(" ")
        print(output)
        
        output = [int(i) for i in output]
        print("Checking the RSSI value in VLC channel: "+str(output))
        #print("CURRENT STATE={}".format(current_state))

        #execute(vlc1)
        if output[2]<80 and current_state=="VLC": #and output[1]>935 and output[2] <20 and output[0]<1089: # and current_state=="VLC":
            execute(vlc1)
            print("Switching to WiFi channel \n")
            start_time = time.time()
            execute(wifi_link)
            vlcToWiFi_time = time.time() - start_time
            print("HANDOVER TIME VLC to WiFi : " + str(vlcToWiFi_time)+" s")
            current_state="WIFI"
            
        elif output[2]>50 and current_state=="WIFI":
            #if current_state=="WIFI":
            execute(vlc1)
            print("Switching to VLC channel \n")
            start_time = time.time()
            execute(vlc_link)
            wifiToVlc_time = time.time() - start_time
            print("HANDOVER TIME WiFi to VLC : " + str(wifiToVlc_time)+" s")
            current_state="VLC"
        time.sleep(T)

@fab.task
def iperf():
    #fab.sudo('nohup %s &> /dev/null &' % "iperf -c 192.168.10.2 -u -b 1000M -l 800 -p 10003 -t 100000")
    #fab.run("nohup iperf -c 192.168.10.2 -u -b 1000M -l 800 -p 10003 -t 100000 --daemon")
    fab.sudo("python3 iperf.py")

#Handover
@fab.task
def handover(capture=True):
    current_state="VLCT1"
    while 1:
        execute(vlc2)
        output = execute(getRSSI)
        output=output[list(env.hosts)[0]].split(" ")
        print(output)
        output = [int(i) for i in output]
        print("Checking the RSSI value in VLC channel: "+ str(output))
        time.sleep(1)
        
        if output[2]<50 and current_state=="VLCT1":
            start_time = time.time()
            execute(vlc3)
            execute(iperf)
            #time.sleep(3)
            V1ToV2_time = time.time() - start_time
            print("HANDOVER TIME V1 to V2 : " + str(V1ToV2_time)+" s")
            time.sleep(3)
            execute(vlc1)
            execute(stop_iperf)
            current_state="VLCT2"
         
           
        elif output[2]<50 and current_state=="VLCT2":
        
            start_time = time.time()
            execute(vlc1)
            execute(iperf)
            #time.sleep(3)
            V2ToV1_time = time.time() - start_time
            print("HANDOVER TIME V2 to V1 : " + str(V2ToV1_time)+" s")
            time.sleep(3)
            execute(vlc3)
            execute(stop_iperf)
            current_state="VLCT1"
         
           
          
        
        