import fabric.api as fab
import fabric.utils
from fabric.api import run, env, execute, roles, settings, hide
from fabric.context_managers import cd
import time
import numbers
from datetime import date
import pandas as pd
import art
import random
import textwrap

#env.hosts={'debian@10.8.10.5'}
env.roledefs = { 'vlc1': ['debian@10.8.10.5'], 'vlc2': ['debian@10.8.10.6'] }
env.passwords = { 'debian@10.8.10.5:22':'temppwd', 'debian@10.8.10.8:22':'temppwd' }

#nice workaround solution to embed the host access parameters as a fabric task
@fab.task
def vlc1():
    env.hosts={'debian@10.8.10.5'}
    env.passwords = {'debian@10.8.10.5:22':'temppwd'}

@fab.task
def vlc3():
    env.hosts={'debian@10.8.10.9'}
    env.passwords = {'debian@10.8.10.9:22':'temppwd'}
    
@fab.task
def vlc2():
    env.hosts={'debian@10.8.10.6'}
    env.passwords = {'debian@10.8.10.6:22':'temppwd'}

@fab.task
def getRSSI():
    output = fab.sudo("python3 getRSSI.py")
    #output=int(output)
    #output = output[list(env.hosts)[0]].split(" ")
    #output = [int(i) for i in output]
    return output

@fab.task
def start_iperf_client(type=""):
    #fab.run("killall -9 iperf")
    if type=="vlc":
        command = 'nohup %s &> /dev/null &' % "iperf -c 192.168.0.2 -u -b 1M -l 800 -p 10001 -t 100000"
    elif type=="wifi":
        command = 'nohup %s &> /dev/null &' % "iperf -c 10.0.0.13 -u -b 1M -l 800 -p 10002 -t 100000"
    else:
        command = 'nohup %s &> /dev/null &' % "iperf -c 192.168.10.2 -u -b 1000M -l 800 -p 10001 -t 100000"
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
        #command = "iperf -u -l 800 -s -i3 -B 10.0.0.13 -p 10002"
    else:
        rx_host="192.168.10.2"
        command = "iperf -u -l 800 -s -i3 -B 192.168.10.2 -p 10001"

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
    fab.sudo("connmanctl connect wifi_7c8bca091d71_6f70656e564c432d73736964_managed_none")

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
        v2w_time=fab.sudo("./wifi_link.sh")
        return v2w_time

#@roles('vlc1')
@fab.task
def vlc_link():
    #fab.sudo = ("route add -net 192.168.10.0 gw 192.168.0.1 netmask 255.255.255.0 dev vlc0")
    #fab.sudo = ("route del -net 192.168.10.0 gw 192.168.12.1 netmask 255.255.255.0 dev ap0")
    #fab.sudo = ("route del -net 192.168.10.0 gw 192.168.12.1 netmask 255.255.255.0 dev ap0 && route add -net 192.168.10.0 gw 192.168.0.1 netmask 255.255.255.0 dev vlc0")
    with cd('/home/debian/OpenVLC/Latest_Version/'):
        w2v_time=fab.sudo("./vlc_link.sh")
        return w2v_time

#The stream will make a jump to different network after 10 seconds
@fab.task
def schedule_controller():
    while True:
        start_time = time.time()
        execute('vlc_link')
        wifiToVLC_time = time.time() - start_time
        print("Wifi to VLC : " + str(wifiToVLC_time))
        
        time.sleep(5)
        
        start_time2 = time.time()
        execute('wifi_link')
        vlcToWifi_time = time.time() - start_time2
        print("VLC to WiFi : " + str(wifiToVLC_time))
        time.sleep(5)

@fab.task
def iperf1():
    #fab.sudo=("iperf -c 192.168.0.2 -u -b 1M -l 800 -p 10001 -t 100000")
    fab.sudo = ('nohup %s &> /dev/null &' % "iperf -c 192.168.0.2 -u -b 10M -l 800 -p 10003 -t 100000")

@fab.task
def iperf2():
    #fab.sudo=("iperf -u -l 800 -s -i3 -B 192.168.0.2 -p 10001")
    fab.sudo = ('iperf -u -l 800 -s -i3 -B 192.168.0.2 -p 10003')

#@roles('vlc1')
@fab.task
def dumpUDP():
    with settings( hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
    #with cd('/home/debian/OpenVLC/Latest_Version/'):
        #execute(kill_dumpUDP)
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
    #print("link quality = %d" %link_quality)
    #print("signal_level = %d" %signal_level)
    #print("noise_level = %d" %noise_level)
    #if link_quality >= 90:
    #    print("Link quality channel: %d >=90 \n" %(link_quality))
    #else:
    #    print("Link quality channel: %d <90 \n" %(link_quality))
    return link_quality,signal_level,noise_level
    
    
@fab.task
def link_quality(capture=True):
    link_quality = int(fab.sudo('iwconfig wlan0 | grep -o "Link Quality=[0-9]*" | sed -e "s/.*=//g"'))
    return link_quality
    
@fab.task
def signal_level(capture=True): 
    signal_level = int(fab.sudo('iwconfig wlan0 | grep -o "Signal level=-[0-9]*" | sed -e "s/.*=//g"'))
    return signal_level

@fab.task
def noise_level(capture=True):
    noise_level = int(fab.sudo('iwconfig wlan0 | grep -o "Noise level=[0-9]*" | sed -e "s/.*=//g"'))
    return noise_level

@fab.task
def iwifi(capture=True):
    iwifi=fab.sudo("python3 iwifi.py")
    iwifi=iwifi.split()
    #print(iwifi)
    #print(type(iwifi))
    #print("Bandwidth = %s, Jitter = %s, LossP = %s " %(iwifi[0], iwifi[1], iwifi[2]))
    return iwifi

#Intelligent Control
@fab.task
def icontrol(capture=True):
    T=1
    Twatchdog=2
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
        output = [int(i) for i in output]
        print("Checking the RSSI value in VLC channel 1: "+str(output))
        time.sleep(2)
        #print("CURRENT STATE={}".format(current_state))

        #execute(vlc1)
        if output[2]<50 and current_state=="VLC": #and output[1]>935 and output[2] <20 and output[0]<1089: # and current_state=="VLC":
            execute(vlc1)
            execute(kill_dumpUDP)
            print("Switching to WiFi channel \n")
            
            v2w_time=execute(wifi_link)
            #v2w_time=[num for num in v2w_time if isinstance(num, numbers.Number)]
            #print(v2w_time)
            print("HANDOVER TIME VLC to WiFi : " + str(v2w_time)+" ms")
            current_state="WIFI"
            
        elif output[2]>50 and current_state=="WIFI":
            execute(vlc1)
            
            print("Switching to VLC channel \n")
            
            w2v_time=execute(vlc_link)
            #w2v_time=[num for num in w2v_time if isinstance(num, numbers.Number)]
            print("HANDOVER TIME WiFi to VLC : " + str(w2v_time)+" ms")
            current_state="VLC"
        time.sleep(T)

@fab.task
def iperf(capture=True):
    #fab.sudo('nohup %s &> /dev/null &' % "iperf -c 192.168.10.2 -u -b 1000M -l 800 -p 10003 -t 100000")
    #fab.run("nohup iperf -c 192.168.10.2 -u -b 1000M -l 800 -p 10003 -t 100000 --daemon")
    i=fab.sudo("python3 iperf.py")
    return i

#Handover
@fab.task
def handover(capture=True):
    current_state="VLCT1"
    data=[]
    i=0
    i2=0
    while 1:
        execute(vlc2)
        output = execute(getRSSI)
        output=output[list(env.hosts)[0]].split(" ")
        print(output)
        output = [int(i) for i in output]
        print("Checking the RSSI value in VLC channel: "+ str(output))
        time.sleep(1)
        i=0
        i2=0
        data.append([output])
        import pandas as pd
        df = pd.DataFrame(data)
        print(df)
        
        if output[2]<50 and current_state=="VLCT1":
            
            execute(vlc3)
            start_time = time.time()
            i=execute(iperf)
            print(i)
            #time.sleep(3)
            #V1ToV2_time = time.time() - start_time
            print("HANDOVER TIME V1 to V2 : " + str(i)+" ms")
            time.sleep(1)
            execute(vlc1)
            execute(stop_iperf)
            current_state="VLCT2"
         
           
        elif output[2]<50 and current_state=="VLCT2":
        
            execute(vlc1)
            start_time = time.time()
            i2=execute(iperf)
            print(i2)
            #time.sleep(3)
            #V2ToV1_time = time.time() - start_time
            print("HANDOVER TIME V2 to V1 : " + str(i2)+" ms")
            time.sleep(1)
            execute(vlc3)
            execute(stop_iperf)
            current_state="VLCT1"
            
            
#Intelligent Control
@fab.task
def icontrol2(capture=True):
    T=1
    Twatchdog=2
    execute(vlc1)
    execute(vlc_link)
    current_state="VLC1"
    time.sleep(T)

    while 1:
        #Watchdog for VLC
        execute(vlc2)
        output = execute(getRSSI)
        output=output[list(env.hosts)[0]].split(" ")
        output = [int(i) for i in output]
        print("Checking the RSSI value in VLC channel 1: "+str(output))
        time.sleep(2)
        #print("CURRENT STATE={}".format(current_state))
        
        execute(vlc3)
        execute(dumpUDP)
        time.sleep(1)
        execute(vlc2)
        output_2 = execute(getRSSI)
        output_2=output_2[list(env.hosts)[0]].split(" ")
        output_2 = [int(i) for i in output_2]
        print("Checking the RSSI value in VLC channel 2: "+str(output_2))
        time.sleep(2)

        if current_state=="WIFI":
            if output[2]>50 and output_2[2]<50:
                execute(vlc1)
                execute(vlc_link)
                current_state="VLC1"
            elif output[2]<50 and output_2[2]>50:
                execute(vlc1)
                execute(vlc_link)
                current_state="VLC2"
            elif output[2]<50 and output_2[2]<50:
                execute(vlc1)
                execute(vlc_link)
                current_state="VLC1"
                
        elif current_state=="VLC1": 
            if output[2]<50 and output_2[2]>50:
                execute(vlc3)
                execute(iperf)
                time.sleep(3)
                execute(vlc1)
                execute(stop_iperf)
                current_state="VLC2"
                print("Currently in VLC2")
                
            elif output[2]<50 and output_2[2]<50:
                execute(vlc1)
                execute(wifi_link)
                current_state="WIFI"
                
        elif current_state=="VLC2": 
            if output[2]>50 and output_2[2]<50:
                execute(vlc1)
                execute(iperf)
                time.sleep(3)
                execute(vlc3)
                execute(stop_iperf)
                current_state="VLC1"
                print("Currently in VLC1")
                
            elif output[2]<50 and output_2[2]<50:
                execute(vlc1)
                execute(wifi_link)
                current_state="WIFI"

        time.sleep(T)
        
#Test collecting data
@fab.task
def data(capture=True):
    data = []
    link=0
    signal=0
    noise=0
    #tt=0
    
    while 1:
        execute(vlc2)
        output = execute(getRSSI)
        output=output[list(env.hosts)[0]].split(" ")
        output = [int(i) for i in output]
        #print("Checking the RSSI value in VLC channel 1: "+str(output))
        
        
        link=execute(link_quality)
        link=link['debian@10.8.10.6']
        signal=execute(signal_level)
        signal=signal['debian@10.8.10.6']
        noise=execute(noise_level)
        noise=noise['debian@10.8.10.6']
        #tt+=1
        
        #execute(vlc1)
        #iwi=execute(iwifi)
        #iwi=iwi['debian@10.8.10.5']
        #print(iwi)
        
        #data.append([tt,output[0],output[1],output[2],link,signal,noise,iwi[0],iwi[1],iwi[2]])
        #data.append([tt,output[0],output[1],output[2],link,signal,noise])
        data.append([output[0],output[1],output[2],link,signal,noise])    
        #df = pd.DataFrame(data,columns=["Time (s)","Max_RSSI_VLC","Min_RSSI_VLC","Std_RSSI_VLC", "link_quality_wifi","signal_level_wifi","noise_level_wifi","bandwidth_wifi", "jitter_wifi", "lossPacket_wifi"])
        #df = pd.DataFrame(data,columns=["Time (s)","Max_RSSI_VLC","Min_RSSI_VLC","Std_RSSI_VLC", "link_quality_wifi","signal_level_wifi","noise_level_wifi"])
        df = pd.DataFrame(data,columns=["Max_RSSI_VLC","Min_RSSI_VLC","Std_RSSI_VLC", "link_quality_wifi","signal_level_wifi","noise_level_wifi"])

        #print(df)
        df.to_csv('Palermo6.csv')
        
        time.sleep(2)
        
@fab.task
def getRSSI_infi():
    while True:
        output = fab.sudo("python3 getRSSI.py")
    #output=int(output)
    #output = output[list(env.hosts)[0]].split(" ")
    #output = [int(i) for i in output]
        time.sleep(1)
        
        
        
#Intelligent Control test
@fab.task
def icontrol_demo(capture=True):
    T=3
    Twatchdog=1
    execute(vlc1)
    execute(vlc_link)
    current_state="VLC"
    time.sleep(T)

    while 1:
        #Watchdog for VLC
        if current_state=="WIFI":
            execute(vlc1)
            execute(dumpUDP)
            execute(vlc_link)
            #time.sleep(Twatchdog)
        #RX
        execute(vlc2)
        output = execute(getRSSI)
        output=output[list(env.hosts)[0]].split(" ")
        output = [int(i) for i in output]
        #print("Checking the RSSI value in VLC channel 1: "+str(output))
        text_ascii = art.text2art("Checking the RSSI value in VLC channel 1: ")
        output_ascii = art.text2art(str(output))
        print("Checking the RSSI value in VLC channel 1: ")
        print(output_ascii)
        #print("CURRENT STATE={}".format(current_state))

        #execute(vlc1)
        if output[2]<30 and current_state=="VLC": #and output[1]>935 and output[2] <20 and output[0]<1089: # and current_state=="VLC":
            execute(vlc1)
            execute(kill_dumpUDP)
            text_ascii_1 = art.text2art("Switch to WiFi channel")
            print(text_ascii_1)
            
            v2w_time=execute(wifi_link)
            #v2w_time=[num for num in v2w_time if isinstance(num, numbers.Number)]
            #print(v2w_time)
            print("HANDOVER TIME VLC to WiFi : " + str(v2w_time)+" ms")
            current_state="WIFI"
            
        elif output[2]>30 and current_state=="WIFI":
            execute(vlc1)
            
            text_ascii_2 = art.text2art("Switch to VLC channel")
            print(text_ascii_2)
            
            w2v_time=execute(vlc_link)
            #w2v_time=[num for num in w2v_time if isinstance(num, numbers.Number)]
            print("HANDOVER TIME WiFi to VLC : " + str(w2v_time)+" ms")
            current_state="VLC"
        time.sleep(T)


#Intelligent Control test 2023
@fab.task     
def icontrol_2023(capture=True):
    T=3
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
            execute(vlc_link)
            time.sleep(Twatchdog)
        #RX
        execute(vlc2)
        output = execute(getRSSI)
        output=output[list(env.hosts)[0]].split(" ")
        output = [int(i) for i in output]
        #print("Checking the RSSI value in VLC channel 1: "+str(output))
        text_ascii = art.text2art("Checking the RSSI value in VLC channel 1: ")
        output_ascii = art.text2art(str(output))
        print("Checking the RSSI value in VLC channel 1: ")
        print(output_ascii)
        #print("CURRENT STATE={}".format(current_state))
        time.sleep(Twatchdog)

        #execute(vlc1)
        if output[2]<30 and current_state=="VLC":
            execute(vlc1)
            execute(kill_dumpUDP)
            text_ascii_1 = art.text2art("Switch to WiFi channel")
            print(text_ascii_1)
            
            v2w_time=execute(wifi_link)
            #v2w_time=[num for num in v2w_time if isinstance(num, numbers.Number)]
            #print(v2w_time)
            print("HANDOVER TIME VLC to WiFi : " + str(v2w_time)+" ms")
            current_state="WIFI"
            
            # Generate random number from 1 to 10
            random_number = random.randint(1, 10)
            random_number_ascii = art.text2art(str(random_number))
            print("Random number generated: ")
            print(random_number_ascii)
            
        elif output[2]>30 and current_state=="WIFI":
            execute(vlc1)
            
            text_ascii_2 = art.text2art("Switch to VLC channel")
            print(text_ascii_2)
            
            w2v_time=execute(vlc_link)
            #w2v_time=[num for num in w2v_time if isinstance(num, numbers.Number)]
            print("HANDOVER TIME WiFi to VLC : " + str(w2v_time)+" ms")
            current_state="VLC"
            
            # Generate random number from 1 to 10
            random_number = random.randint(1, 10)
            random_number_ascii = art.text2art(str(random_number))
            print("Random number generated: ")
            print(random_number_ascii)

        time.sleep(T)
        


import random

# List of facts about popular people in Italy
facts = [
    
]

football_questions = [
    "This Italian goalkeeper, considered one of the best of all time, played for Juventus and the Italian national team. Who is he?",
    "This Italian footballer, known as 'Il Divin Codino', is a former forward who played for clubs like AC Milan and Inter Milan. Who is he?",
    "This Italian striker, nicknamed 'Pippo', played for AC Milan and the Italian national team, scoring crucial goals in multiple competitions. Who is he?",
    "This Italian footballer, a legendary midfielder, played for AS Roma and the Italian national team, wearing the number 10 jersey. Who is he?",
    "This Italian defender, known for his tough tackling and leadership, played for AC Milan and the Italian national team. Who is he?",
    "This Italian midfielder, known for his vision and passing abilities, played for Juventus and the Italian national team. Who is he?",
    "This Italian footballer, a prolific striker, played for clubs like Napoli, Juventus, and the Italian national team. Who is he?",
    "This Italian midfielder, known for his free-kick expertise, played for Lazio, Inter Milan, and the Italian national team. Who is he?",
    "This Italian footballer, a versatile defender, played for clubs like Lazio, Inter Milan, and the Italian national team. Who is he?",
    "This Italian manager, a former midfielder, coached clubs like Juventus and Inter Milan, as well as the Italian national team. Who is he?",
    "This Italian striker, known for his acrobatic goals, played for clubs like Fiorentina, Roma, and the Italian national team. Who is he?",
    "This Italian defender, a key figure in the 2006 World Cup-winning team, played for clubs like Parma, Juventus, and the Italian national team. Who is he?",
    "This Italian midfielder, known for his tenacity and stamina, played for clubs like AC Milan, Juventus, and the Italian national team. Who is he?",
    "This Italian footballer, a talented winger, played for clubs like AS Roma, AC Milan, and the Italian national team. Who is he?",
    "This Italian striker, known for his goal-scoring prowess, played for clubs like AC Milan, Chelsea, and the Italian national team. Who is he?",
    "In which year did Italy win their first FIFA World Cup?",
    "In which year did Italy win their fourth and most recent FIFA World Cup?",
    "This Italian football club, one of the most successful in Italy, is based in Turin. Which club is it?",
    "This Italian footballer scored the winning penalty in the 2006 FIFA World Cup Final against France. Who is he?",
    "This Italian footballer, a defender, scored the equalizing goal in the 2006 FIFA World Cup Final against France. Who is he?",
    "This Italian footballer, a legendary goalkeeper, played for clubs like Parma and AC Milan, and the Italian national team. Who is he?",
    "This Italian midfielder, known for his exceptional playmaking skills, played for clubs like Brescia, AC Milan, and the Italian national team. Who is he?",
    "This Italian footballer, a talented winger, played for clubs like Juventus, Fiorentina, and the Italian national team. Who is he?",
    "This Italian striker, known for his speed and goal-scoring abilities, played for clubs like Torino, AC Milan, and the Italian national team. Who is he?",
    "This Italian footballer, a strong and versatile defender, played for clubs like AC Milan, Juventus, and the Italian national team. Who is he?",
    "This Italian midfielder, known for his leadership and work rate, played for clubs like Napoli, Parma, and the Italian national team. Who is he?",
    "This Italian footballer, a skillful winger, played for clubs like Lazio, Inter Milan, and the Italian national team. Who is he?",
    "This Italian striker, known for his powerful shots and aerial abilities, played for clubs like Sampdoria, Lazio, and the Italian national team. Who is he?",
    "This Italian footballer, a solid and reliable defender, played for clubs like AS Roma, Real Madrid, and the Italian national team. Who is he?",
    "This Italian midfielder, known for his creativity and technique, played for clubs like AC Milan, Paris Saint-Germain, and the Italian national team. Who is he?",
    "This Italian footballer, a talented attacking midfielder, played for clubs like Udinese, Juventus, and the Italian national team. Who is he?",
    "This Italian striker, known for his goal-scoring instincts, played for clubs like Piacenza, AS Roma, and the Italian national team. Who is he?",
    "This Italian footballer, a versatile and skilled midfielder, played for clubs like Inter Milan, AC Milan, and the Italian national team. Who is he?",
    "This Italian midfielder, known for his defensive abilities and leadership, played for clubs like Juventus, Monaco, and the Italian national team. Who is he?",
    "This Italian footballer, a prolific striker, played for clubs like Palermo, Napoli, and the Italian national team. Who is he?",
    "This Italian defender, known for his tactical intelligence and ability to read the game, played for clubs like AC Milan, Chelsea, and the Italian national team. Who is he?",
    "This Italian footballer, a talented left-back, played for clubs like AS Roma, Inter Milan, and the Italian national team. Who is he?",
    "This Italian midfielder, known for his set-piece skills and long-range shooting, played for clubs like Udinese, Napoli, and the Italian national team. Who is he?",
    "This Italian footballer, a skilled and reliable goalkeeper, played for clubs like Genoa, Napoli, and the Italian national team. Who is he?",
    "This Italian defender, known for his aerial abilities and leadership, played for clubs like Palermo, Juventus, and the Italian national team. Who is he?",
    "This Italian footballer, a talented forward, played for clubs like Lazio, Torino, and the Italian national team. Who is he?",
    "This Italian midfielder, known for his vision and passing abilities, played for clubs like Atalanta, Fiorentina, and the Italian national team. Who is he?",
    "This Italian footballer, a versatile and hard-working midfielder, played for clubs like AC Milan, Paris Saint-Germain, and the Italian national team. Who is he?",
    "This Italian striker, known for his clinical finishing, played for clubs like Cagliari, Juventus, and the Italian national team. Who is he?",
    "This Italian footballer, a skillful and creative attacking midfielder, played for clubs like AC Milan, Juventus, and the Italian national team. Who is he?",
]

modern_football_questions = [
    "This Italian midfielder, known for his vision and passing abilities, played for clubs like Paris Saint-Germain and Inter Milan, and the Italian national team. Who is he?",
    "This Italian striker, known for his powerful shots and goal-scoring instincts, played for clubs like Torino, AC Milan, and the Italian national team. Who is he?",
    "This Italian footballer, a talented goalkeeper, played for clubs like AC Milan, Paris Saint-Germain, and the Italian national team. Who is he?",
    "This Italian defender, known for his leadership and tactical intelligence, played for clubs like Juventus, AC Milan, and the Italian national team. Who is he?",
    "This Italian footballer, a versatile midfielder, played for clubs like AS Roma, Inter Milan, and the Italian national team. Who is he?",
    "This Italian midfielder, known for his defensive abilities and work rate, played for clubs like Napoli, Chelsea, and the Italian national team. Who is he?",
    "This Italian footballer, a skillful winger, played for clubs like Sassuolo, Juventus, and the Italian national team. Who is he?",
    "This Italian striker, known for his goal-scoring abilities and creativity, played for clubs like Napoli, Juventus, and the Italian national team. Who is he?",
    "This Italian footballer, a solid and reliable defender, played for clubs like Torino, AC Milan, and the Italian national team. Who is he?",
    "This Italian midfielder, known for his technique and playmaking skills, played for clubs like Juventus, Zenit St. Petersburg, and the Italian national team. Who is he?",
    "This Italian footballer, a talented goalkeeper, played for clubs like Genoa, Napoli, and the Italian national team. Who is he?",
    "This Italian defender, known for his aerial abilities and strong tackling, played for clubs like Juventus, Inter Milan, and the Italian national team. Who is he?",
    "This Italian footballer, a versatile and skilled midfielder, played for clubs like AS Roma, Paris Saint-Germain, and the Italian national team. Who is he?",
    "This Italian midfielder, known for his set-piece skills and long-range shooting, played for clubs like Udinese, Napoli, and the Italian national team. Who is he?",
    "This Italian footballer, a prolific striker, played for clubs like Palermo, Napoli, and the Italian national team. Who is he?",
    "In which year did Italy reach the UEFA European Championship Final but lost to Spain?",
    "In which year did Italy reach the UEFA European Championship Final but lost to France?",
    "This Italian football club won the Serie A title in the 2010-2011 season. Which club is it?",
    "This Italian football club won the Serie A title in the 2019-2020 season. Which club is it?",
    "This Italian footballer scored the winning goal for Italy in the UEFA Euro 2020 Round of 16 match against Austria. Who is he?",
    "This Italian footballer scored two goals in the UEFA Euro 2020 semi-final match against Spain. Who is he?",
    "This Italian goalkeeper saved crucial penalties in the UEFA Euro 2020 semi-final and final shootouts. Who is he?",
    "This Italian defender scored a crucial goal in the UEFA Euro 2020 quarter-final match against Belgium. Who is he?",
    "This Italian footballer scored Italy's opening goal in the UEFA Euro 2020 final against England. Who is he?",
    "In which year did Italy win the UEFA European Championship for the second time in their history?"
]

popular_italian_questions = [
    # Footballers
    "This legendary Italian goalkeeper played most of his career at Juventus and later moved to Paris Saint-Germain. Who is he?",
    "This Italian midfielder, known for his exceptional playmaking skills, played for clubs like Brescia, AC Milan, and the Italian national team. Who is he?",
    "This Italian defender, nicknamed 'The Berlin Wall', played for clubs like Lazio and Inter Milan, and the Italian national team. Who is he?",
    "This Italian striker, known for his speed and goal-scoring abilities, played for clubs like Torino, AC Milan, and the Italian national team. Who is he?",
    "This Italian footballer, a strong and versatile defender, played for clubs like AC Milan and the Italian national team. Who is he?",
    
    # Actors and Actresses
    "Which Italian actress starred in the 1960 film 'La Dolce Vita' directed by Federico Fellini?",
    "This Italian actor starred in the 1988 film 'Cinema Paradiso' directed by Giuseppe Tornatore. Who is he?",
    "This Italian actress gained international fame for her roles in films like 'Malèna' and 'The Matrix Reloaded.' Who is she?",
    
    # Singers and Musicians
    "This Italian tenor, one of the most famous opera singers of all time, was part of The Three Tenors. Who is he?",
    "This Italian singer-songwriter is known for his deep voice and romantic ballads. Who is he?",
    "Which Italian operatic pop trio consists of Piero Barone, Ignazio Boschetto, and Gianluca Ginoble?",
    
    # Fashion Designers
    "These two Italian designers founded a luxury fashion house in 1985, known for its bold prints and glamorous designs. Who are they?",
    "This Italian fashion designer founded the luxury fashion house that is synonymous with the Medusa logo. Who is he?",
    
    # Chefs
    "This Italian-American celebrity chef is known for her popular Food Network shows and her Italian cuisine. Who is she?",
    "This Italian chef, restaurateur, and writer is known for his appearances on television shows such as 'MasterChef Italia.' Who is he?",
    
    # Entrepreneurs and Businesspeople
    "This Italian entrepreneur is the founder of the luxury sports car company that bears his name. Who is he?",
    "This Italian businessman is the founder of the global fashion brand known for its jeans and casual wear. Who is he?",
    
    # Directors
    "This Italian film director is known for his distinctive style and films like 'La Dolce Vita' and '8½.' Who is he?",
    "This Italian film director won the Academy Award for Best Foreign Language Film for 'Cinema Paradiso.' Who is he?",
    
    # Artists
    "This Italian street artist is known for his satirical and thought-provoking murals. Who is he?",
    "This Italian contemporary artist is known for his large-scale sculptures and installations. Who is he?"
]

facts_italy_en = [
    "This person is a famous Italian film director, known for movies like 'La Dolce Vita' and '8½'. Who is he?",
    "This individual is a renowned Italian opera composer, best known for works such as 'La Traviata' and 'Aida'. Who is he?",
    "This person is a legendary Italian artist and inventor, famous for masterpieces like 'The Last Supper' and 'Mona Lisa'. Who is he?",
    "This individual is a prominent Italian fashion designer, founder of a luxury fashion house that bears his name. Who is he?",
    "This famous Italian city is known for its network of canals and gondolas. What is it called?",
    "This iconic Italian landmark is known for its unintended tilt. What is it?",
    "This Italian volcano is one of the most active in the world and destroyed the ancient city of Pompeii. What is its name?",
    "This Italian island is the largest in the Mediterranean Sea. What is it called?",
    "This Italian dish consists of a thin, round base of dough topped with tomato sauce, cheese, and various toppings. What is it?",
    "This Italian dessert is made with layers of coffee-soaked ladyfingers and a rich, creamy mascarpone cheese mixture. What is it called?",
    "This Italian city is the birthplace of the Renaissance and home to famous art and architecture. What is it?",
    "This Italian sports car manufacturer, founded in 1947, is known for its prancing horse logo. What is the company's name?",
    "This famous Italian explorer is credited with discovering America in 1492. Who is he?",
    "This Italian scientist is known for his improvements to the telescope and his support of the heliocentric model of the solar system. Who is he?",
    "This Italian-American actor starred in 'The Godfather' and 'Apocalypse Now'. Who is he?",
    "This Italian term refers to a type of pasta that is shaped like small, ridged tubes. What is it called?",
    "This Italian region is famous for its picturesque coastal towns and is a popular tourist destination. What is it?",
    "This Italian liqueur is made from the infusion of lemon peels in alcohol and is often served as a digestif. What is it called?",
    "This Italian city is the capital of the Lombardy region and is known for its fashion and design industries. What is it?",
    "This ancient Roman amphitheater, known for its gladiator battles and other public spectacles, is one of Italy's most iconic landmarks. What is its name?",
]

facts_italy = [
    "1. Questa persona è un famoso regista italiano, noto per film come 'La Dolce Vita' e '8½'. Chi è?",
    "2. Questo individuo è un rinomato compositore d'opera italiano, famoso per opere come 'La Traviata' e 'Aida'. Chi è?",
    "3. Questa persona è un leggendario artista e inventore italiano, famoso per capolavori come 'L'Ultima Cena' e 'La Gioconda'. Chi è?",
    "4. Questo individuo è un importante stilista italiano, fondatore di una casa di moda di lusso che porta il suo nome. Chi è?",
    "5. Questa famosa città italiana è conosciuta per la sua rete di canali e gondole. Come si chiama?",
    "6. Questo iconico monumento italiano è noto per la sua inclinazione involontaria. Cos'è?",
    "7. Questo vulcano italiano è uno dei più attivi al mondo e ha distrutto l'antica città di Pompei. Qual è il suo nome?",
    "8. Questa isola italiana è la più grande del Mar Mediterraneo. Come si chiama?",
    "9. Questo piatto italiano consiste in una base sottile e rotonda di pasta ricoperta di salsa di pomodoro, formaggio e vari ingredienti. Cos'è?",
    "10. Questo dessert italiano è fatto con strati di savoiardi inzuppati nel caffè e una ricca miscela di formaggio mascarpone. Come si chiama?",
    "11. Questa città italiana è la culla del Rinascimento e ospita famose opere d'arte e architettura. Qual è?",
    "12. Questo produttore italiano di auto sportive, fondato nel 1947, è noto per il suo logo con il cavallo rampante. Qual è il nome dell'azienda?",
    "13. Questo famoso esploratore italiano è accreditato per aver scoperto l'America nel 1492. Chi è?",
    "14. Questo scienziato italiano è noto per i suoi miglioramenti al telescopio e per il suo sostegno al modello eliocentrico del sistema solare. Chi è?",
    "15. Questo attore italo-americano ha recitato in 'Il Padrino' e 'Apocalypse Now'. Chi è?",
    "16. Questo termine italiano si riferisce a un tipo di pasta a forma di piccoli tubi rigati. Come si chiama?",
    "17. Questa regione italiana è famosa per le sue pittoresche città costiere ed è una popolare destinazione turistica. Qual è?",
    "18. Questo liquore italiano è fatto con l'infusione di bucce di limone nell'alcool ed è spesso servito come digestivo. Come si chiama?",
    "19. Questa città italiana è la capitale della regione Lombardia ed è conosciuta per le sue industrie della moda e del design. Qual è?",
    "20. Questo antico anfiteatro romano, noto per le sue battaglie di gladiatori e altri spettacoli pubblici, è uno dei monumenti più iconici d'Italia. Qual è il suo nome?",
    "21. Questo famoso scultore italiano è noto per aver creato il 'David' e la 'Pietà'. Chi è?",
    "22. Questa è una tipica insalata italiana a base di pomodori, mozzarella, basilico e olio d'oliva. Come si chiama?",
    "23. Questa torre campanaria si trova a Firenze ed è parte integrante del complesso di Santa Maria del Fiore. Qual è il suo nome?",
    "24. Questo fiume italiano è il più lungo del paese e attraversa diverse città importanti, tra cui Torino e Pavia. Come si chiama?",
    "25. Questa famosa fontana di Roma è uno dei luoghi più iconici della città, dove i visitatori lanciano monete per augurarsi buona fortuna. Qual è il suo nome?",
    "26. Questa famosa opera italiana di Giuseppe Verdi racconta la storia di un amore tragico tra Violetta e Alfredo. Come si chiama?",
    "27. Questa regione italiana è conosciuta per la produzione di vini pregiati come il Barolo e il Barbaresco. Qual è?",
    "28. Questo famoso pittore italiano, uno dei massimi esponenti del Barocco, è noto per le sue opere drammatiche e il suo uso del chiaroscuro. Chi è?",
    "29. Questa famosa competizione ciclistica italiana, che si tiene ogni anno, è una delle più importanti del calendario ciclistico internazionale. Come si chiama?",
    "30. Questo famoso palazzo veneziano si affaccia sul Canal Grande ed è noto per la sua architettura gotica. Qual è il suo nome?",
]

facts_world_100 = [
    "1. Quale è il paese più esteso del mondo?",
    "2. Qual è il fiume più lungo del mondo?",
    "3. Qual è il continente più piccolo del mondo?",
    "4. Qual è la capitale della Francia?",
    "5. Qual è il paese del Sol Levante?",
    "6. Quale famoso monumento si trova a Parigi?",
    "7. Qual è la lingua ufficiale del Brasile?",
    "8. In quale paese si trovano il Colosseo e la Torre di Pisa?",
    "9. Qual è il nome completo del Regno Unito?",
    "10. In quale paese si trovano molte dighe e mulini a vento?",
    "11. Qual è la montagna più alta del mondo?",
    "12. Qual è la capitale degli Stati Uniti d'America?",
    "13. In quale città italiana si trovano i canali e le gondole?",
    "14. Qual è il più grande stato dell'Australia?",
    "15. Quale famosa statua si trova a Rio de Janeiro, in Brasile?",
    "16. Quale piccolo paese si trova tra la Francia e la Spagna?",
    "17. Qual è la capitale della Russia?",
    "18. In quale paese si trovano le Alpi e il CERN?",
    "19. Qual è la lingua più parlata nel mondo?",
    "20. Qual è il deserto più freddo del mondo?",
    "21. Quale paese è il più popoloso del mondo?",
    "22. In quale città si trova la statua della Libertà?",
    "23. Qual è il paese con il maggior numero di lingue parlate?",
    "24. Quale città è la capitale dell'Italia?",
    "25. Qual è il paese più piccolo del mondo?",
    "26. Quale oceano è il più grande del mondo?",
    "27. Quale paese è famoso per i suoi fiordi?",
    "28. Qual è il paese con il maggior numero di piramidi?",
    "29. In quale città si trova il Colosseo?",
    "30. Quale paese è famoso per il tango?",
    "31. Quale città è la capitale della Germania?",
    "32. In quale paese si trova il Taj Mahal?",
    "33. Quale paese è famoso per i suoi canguri?",
    "34. Quale paese è il più piccolo in termini di superficie?",
    "35. In quale città si trova la Torre di Pisa?",
    "36. Quale paese è famoso per i suoi castelli e la birra?",
    "37. Quale città è la capitale del Canada?",
    "38. Quale paese è noto per i suoi geyser e vulcani?",
    "39. Quale paese è famoso per la sua pizza e pasta?",
    "40. Qual è il lago più profondo del mondo?",
    "41. Quale città è la capitale dell'Australia?",
    "42. In quale paese si trova il Machu Picchu?",
    "43. Quale paese è famoso per i suoi elefanti e templi?",
    "44. Qual è il fiume più largo del mondo?",
    "45. In quale città si trova la Basilica di San Pietro?",
    "46. Quale paese è famoso per il flamenco e la corrida?",
    "47. Quale città è la capitale della Cina?",
    "48. In quale paese si trova la Grande Barriera Corallina?",
    "49. Quale paese è famoso per i suoi gorilla di montagna?",
    "50. Quale città è la capitale del Giappone?",
    "51. In quale paese si trova il deserto del Sahara?",
    "52. Quale paese è famoso per il suo caffè e samba?",
    "53. Quale città è la capitale della Francia?",
    "54. In quale paese si trova il monte Kilimangiaro?",
    "55. Quale paese è famoso per i suoi vichinghi?",
    "56. Qual è il paese più freddo del mondo?",
    "57. In quale città si trova il Museo del Louvre?",
    "58. Quale paese è famoso per i suoi mari e spiagge?",
    "59. Quale città è la capitale del Regno Unito?",
    "60. In quale paese si trova la foresta pluviale amazzonica?",
    "61. Quale paese è famoso per i suoi ghiacciai e montagne?",
    "62. Qual è il paese più caldo del mondo?",
    "63. In quale città si trova il British Museum?",
    "64. Quale paese è famoso per la sua cucina piccante?",
    "65. Quale città è la capitale della Spagna?",
    "66. In quale paese si trova il Grand Canyon?",
    "67. Quale paese è famoso per i suoi tram e canali?",
    "68. Qual è il paese più ricco del mondo?",
    "69. In quale città si trova il Museo del Prado?",
    "70. Quale paese è famoso per i suoi vulcani e spiagge?",
    "71. Quale è il paese più densamente popolato al mondo?",
    "72. In quale paese si trova la città di Petra?",
    "73. Quale paese è famoso per i suoi tulipani?",
    "74. Qual è la capitale dell'Argentina?",
    "75. In quale paese si trova la Torre di Londra?",
    "76. Quale paese è famoso per i suoi cioccolatini?",
    "77. Qual è la capitale dell'India?",
    "78. In quale paese si trova la città di Atene?",
    "79. Quale paese è famoso per il suo tequila?",
    "80. Qual è la capitale del Brasile?",
    "81. In quale paese si trova il lago Titicaca?",
    "82. Quale paese è famoso per i suoi panda giganti?",
    "83. Qual è la capitale dell'Egitto?",
    "84. In quale paese si trova la città di Dublino?",
    "85. Quale paese è famoso per i suoi kiwi?",
    "86. Qual è la capitale dell'Austria?",
    "87. In quale paese si trova il fiume Danubio?",
    "88. Quale paese è famoso per i suoi sushi?",
    "89. Qual è la capitale della Norvegia?",
    "90. In quale paese si trova la città di Istanbul?",
    "91. Quale paese è famoso per i suoi orologi?",
    "92. Qual è la capitale della Polonia?",
    "93. In quale paese si trova la città di Copenaghen?",
    "94. Quale paese è famoso per i suoi saune?",
    "95. Qual è la capitale della Svezia?",
    "96. In quale paese si trova la città di Edimburgo?",
    "97. Quale paese è famoso per i suoi waffles?",
    "98. Qual è la capitale della Grecia?",
    "99. In quale paese si trova la città di Praga?",
    "100. Quale paese è famoso per i suoi mari e montagne?",
    "101. Qual è la capitale del Vietnam?",
    "102. Qual è la valuta ufficiale del Vietnam?",
    "103. Come si chiama la zuppa vietnamita più famosa?",
    "104. Qual è il nome del sito patrimonio mondiale dell'UNESCO in Vietnam noto per le sue migliaia di isole calcaree?",
    "105. Quale città vietnamita era precedentemente conosciuta come Saigon?",
    "106. Qual è il nome del famoso mausoleo di Hanoi dove è conservato il corpo di Ho Chi Minh?",
    "107. Qual è il nome del lungo e stretto mare in Vietnam, famoso per le sue spiagge di sabbia dorata?",
    "108. Qual è il nome dell'antica capitale imperiale del Vietnam?",
    "109. Qual è il nome del famoso marchio di caffè vietnamita popolare in tutto il mondo?",
    "110. Quale fiume forma un confine naturale tra Vietnam e Cambogia?",
    "111. Qual è la città più grande del Vietnam per popolazione?",
    "112. Quale famosa guerra ebbe luogo in Vietnam tra il 1955 e il 1975?",
    "113. Qual è la lingua ufficiale del Vietnam?",
    "114. Quale distesa d'acqua si trova a est del Vietnam?",
    "115. La ferrovia dell'Espresso della Riunificazione collega quali due grandi città del Vietnam?",
    "116. Qual è il nome della lunga e stretta striscia di terra che collega il Vietnam del Nord e del Sud, conosciuta come 'ponte di terra'?",
]

popular_vietnam_questions = [
    "1. Qual è la capitale del Vietnam?",
    "2. Qual è la valuta ufficiale del Vietnam?",
    "3. Come si chiama la zuppa vietnamita più famosa?",
    "4. Qual è il nome del sito patrimonio mondiale dell'UNESCO in Vietnam noto per le sue migliaia di isole calcaree?",
    "5. Quale città vietnamita era precedentemente conosciuta come Saigon?",
    "6. Qual è il nome del famoso mausoleo di Hanoi dove è conservato il corpo di Ho Chi Minh?",
    "7. Qual è il nome del lungo e stretto mare in Vietnam, famoso per le sue spiagge di sabbia dorata?",
    "8. Qual è il nome dell'antica capitale imperiale del Vietnam?",
    "9. Qual è il nome del famoso marchio di caffè vietnamita popolare in tutto il mondo?",
    "10. Quale fiume forma un confine naturale tra Vietnam e Cambogia?",
    "11. Qual è la città più grande del Vietnam per popolazione?",
    "12. Quale famosa guerra ebbe luogo in Vietnam tra il 1955 e il 1975?",
    "13. Qual è la lingua ufficiale del Vietnam?",
    "14. Quale distesa d'acqua si trova a est del Vietnam?",
    "15. La ferrovia dell'Espresso della Riunificazione collega quali due grandi città del Vietnam?",
    "16. Qual è il nome della lunga e stretta striscia di terra che collega il Vietnam del Nord e del Sud, conosciuta come 'ponte di terra'?",
]




def display_art_text(text, width=40):
    wrapped_text = textwrap.wrap(text, width=width)
    for line in wrapped_text:
        print(art.text2art(line))
        

def display_art_text2(text, width=40):
    wrapped_text = textwrap.wrap(text, width=width)
    for line in wrapped_text:
        text_ascii = art.text2art(line,"basic")
        print("\033[1;32m" + text_ascii + "\033[0m")
        
def display_art_text22(text, width=40):
    wrapped_text = textwrap.wrap(text, width=width)
    
    # ANSI escape codes for green and yellow text
    green_text = "\033[32m"
    yellow_text = "\033[33m"
    reset_text = "\033[0m"
    bold_text = "\033[1m"

    # Loop counter to alternate between colors
    color_counter = 0

    for line in wrapped_text:
        # Select green or yellow text based on the loop counter
        if color_counter % 2 == 0:
            color_text = green_text
        else:
            color_text = yellow_text

        text_ascii = art.text2art(line, "basic")
        print(f"{bold_text}{color_text}{text_ascii}{reset_text}")

        # Increment the loop counter
        color_counter += 1


        
def display_art_text3(text, width=40):
    wrapped_text = textwrap.wrap(text, width=width)
    for line in wrapped_text:
        text_ascii = art.text2art(line,"banner3")
        print("\033[1;31m" + text_ascii + "\033[0m")


#Intelligent Control test
@fab.task
def icontrol_demo2(capture=True):
    T=1
    Twatchdog=1
    execute(vlc1)
    execute(vlc_link)
    current_state="VLC"
    time.sleep(T)

    while 1:
        #Watchdog for VLC
        if current_state=="WIFI":
            execute(vlc1)
            execute(dumpUDP)
            execute(vlc_link)
            #time.sleep(Twatchdog)
        #RX
        execute(vlc2)
        output = execute(getRSSI)
        output=output[list(env.hosts)[0]].split(" ")
        output = [int(i) for i in output]
        print("Checking the RSSI value in VLC channel 1: "+str(output))
        
        #text_ascii = art.text2art("Checking the RSSI value in VLC channel 1: ")
        #output_ascii = art.text2art(str(output))
        #print(output_ascii)
        #print("CURRENT STATE={}".format(current_state))

        #execute(vlc1)
        if output[2]<30 and current_state=="VLC":
            execute(vlc1)
            execute(kill_dumpUDP)
            #text_ascii_1 = art.text2art("Switch to WiFi channel")
            #print(text_ascii_1)
            display_art_text3("Switch to WiFi channel")
            
            v2w_time=execute(wifi_link)
            #v2w_time=[num for num in v2w_time if isinstance(num, numbers.Number)]
            #print(v2w_time)
            print("HANDOVER TIME VLC to WiFi : " + str(v2w_time)+" ms")
            current_state="WIFI"
            
            # Show a random fact about a popular person in Italy
            random_fact = random.choice(facts_world_100)
            print("Random fact about the World:")
            display_art_text22(random_fact)
            
        elif output[2]>30 and current_state=="WIFI":
            execute(vlc1)
            
            #text_ascii_2 = art.text2art("Switch to VLC channel")
            #print(text_ascii_2)
            display_art_text3("Switch to VLC channel")
            
            w2v_time=execute(vlc_link)
            #w2v_time=[num for num in w2v_time if isinstance(num, numbers.Number)]
            print("HANDOVER TIME WiFi to VLC : " + str(w2v_time)+" ms")
            current_state="VLC"
            
            # Show a random fact about a popular person in Italy
            random_fact = random.choice(facts_world_100)
            print("Random fact about the World:")
            display_art_text22(random_fact)

        time.sleep(T)
