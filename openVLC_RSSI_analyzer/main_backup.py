# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


#Next experiments:
#1. out of box: 0.5m
#2. out of box: 1m
#3. out of box: 1.5m
#4. out of box: 2m
#5. out of box: 2m + light interferer (ex smartphone lamp...)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


#cwd = os.getcwd()
#print(cwd)

filename_no = "E:\\Fab_OpenVLC\\openVLC_RSSI_analyzer\\raw\\test_no.raw"
filename_05m = "E:\\Fab_OpenVLC\\openVLC_RSSI_analyzer\\raw\\test_05m.raw"
filename_05i = "E:\\Fab_OpenVLC\\openVLC_RSSI_analyzer\\raw\\test_05idle.raw"

filename_1m = "E:\\Fab_OpenVLC\\openVLC_RSSI_analyzer\\raw\\test_1m.raw"

filename_2m = "E:\\Fab_OpenVLC\\openVLC_RSSI_analyzer\\raw\\test_2m.raw"
filename_3m = "E:\\Fab_OpenVLC\\openVLC_RSSI_analyzer\\raw\\test_3m.raw"
filename_maxdist = "E:\\Fab_OpenVLC\\openVLC_RSSI_analyzer\\raw\\test_maxdist.raw"

#filename_iperf_1 = "raw/outbox_1m_iperf_nlos.raw"
#filename_idle_1_5 = "E:\\Fab_OpenVLC\\openVLC_RSSI_analyzer\\raw\\test_max.raw"
#filename_iperf_1_5 = "raw/outbox_1_5m_iperf_nlos.raw"

def get_rssi(filename):
    df = pd.read_csv(filename,skiprows=23, sep=" ",names=["pos", "1", "2", "3","4","5"])
    del df["pos"]
    del df["5"]
    rssi_array=df.to_numpy().flatten()
    rssi=[int(rssi_array[i],16) for i in range(len(rssi_array))]
    return rssi

def main():

    rssi_no = get_rssi(filename_no)
    rssi_05m = get_rssi(filename_05m)
    print(rssi_05m)
    
    
    rssi_05i = get_rssi(filename_05i)
    rssi_1m = get_rssi(filename_1m)
    rssi_2m = get_rssi(filename_2m)
    rssi_3m = get_rssi(filename_3m)
    rssi_max = get_rssi(filename_maxdist)
    
    #rssi_iperf_0_5=get_rssi(filename_iperf_0_5)
    #rssi_idle_1=get_rssi(filename_idle_1)
    #rssi_iperf_1=get_rssi(filename_iperf_1)
    #rssi_idle_1_5=get_rssi(filename_idle_1_5)
    #rssi_iperf_1_5=get_rssi(filename_iperf_1_5)
    fig = plt.figure()

    #Initialise the subplot function using number of rows and columns
    #figure, axis = plt.subplots(2, 2)
        
    t1= [ np.max(rssi_05m[1:-1]),np.max(rssi_1m[1:-1]), np.max(rssi_2m[1:-1]), np.max(rssi_3m[1:-1]), np.max(rssi_max[1:-1]), np.max(rssi_no[1:-1]),np.max(rssi_05i[1:-1])]
    t2= [ np.min(rssi_05m[1:-1]),np.min(rssi_1m[1:-1]), np.min(rssi_2m[1:-1]), np.min(rssi_3m[1:-1]), np.min(rssi_max[1:-1]), np.min(rssi_no[1:-1]),np.min(rssi_05i[1:-1])]
    t3= [ np.var(rssi_05m[1:-1]),np.var(rssi_1m[1:-1]), np.var(rssi_2m[1:-1]), np.var(rssi_3m[1:-1]), np.var(rssi_max[1:-1]), np.var(rssi_no[1:-1]),np.var(rssi_05i[1:-1])]

    plt.plot(rssi_idle_0_5[1:-1],label="Max distance")
    #plt.plot(rssi_iperf_0_5[1:-1],label="IPERF 0.5")
    print(np.max(rssi_max[1:-1]))
    print(np.min(rssi_max[1:-1]))
    #plt.plot(rssi_idle_1[1:-1],label="No connection")
    #plt.plot(rssi_iperf_1[1:-1],label="IPERF 1")

    #plt.plot(rssi_idle_1_5[1:-1],label="Max 400")
    #plt.plot(rssi_iperf_1_5[1:-1],label="IPERF 1.5")
    x = np.array([0.5, 1, 2.1, 3, "4.2(max)", "out range","0.5i"])

    
    plt.plot(x,t1, label="max RSSI values")
    plt.plot(x,t2, label="min RSSI values")
    plt.plot(x,t3, label="variance values")


    plt.legend()
    plt.grid()
    plt.xlabel("Distance")
    plt.ylabel("RSSI level")
    #plt.xlim(0,300)
    #plt.ylim(800,1200)
    fig.savefig("IDLE vs IPERF RSSI TEST test var.pdf")
    fig.savefig("IDLE vs IPERF RSSI TEST test var.png")
    plt.show()


#    print("wait...")
# Press the green button in the gutter to run the script.
#if __name__ == '__main__':
#    main()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/






####20/05/2022#####
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


#Next experiments:
#1. out of box: 0.5m
#2. out of box: 1m
#3. out of box: 1.5m
#4. out of box: 2m
#5. out of box: 2m + light interferer (ex smartphone lamp...)


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import statistics

filename_idle="raw/dump_idle.raw"
filename_iperf="raw/dump_iperf_400K.raw"

filename_05m = "E:\\Fab_OpenVLC\\openVLC_RSSI_analyzer\\raw\\05m.raw"
filename_1m = "E:\\Fab_OpenVLC\\openVLC_RSSI_analyzer\\raw\\1m.raw"
filename_15m = "E:\\Fab_OpenVLC\\openVLC_RSSI_analyzer\\raw\\15m.raw"

filename_t0 = "E:\\Fab_OpenVLC\\IMDEA\\d0.raw"
filename_t10 = "E:\\Fab_OpenVLC\\IMDEA\\d10.raw"
filename_t20 = "E:\\Fab_OpenVLC\\IMDEA\\d20.raw"
filename_t30 = "E:\\Fab_OpenVLC\\IMDEA\\d30.raw"
filename_t40 = "E:\\Fab_OpenVLC\\IMDEA\\d40.raw"
filename_t50 = "E:\\Fab_OpenVLC\\IMDEA\\d50.raw"
filename_t60 = "E:\\Fab_OpenVLC\\IMDEA\\d60.raw"
filename_t70 = "E:\\Fab_OpenVLC\\IMDEA\\d70.raw"
filename_t80 = "E:\\Fab_OpenVLC\\IMDEA\\d80.raw"
filename_t90 = "E:\\Fab_OpenVLC\\IMDEA\\d90.raw"
filename_t100 = "E:\\Fab_OpenVLC\\IMDEA\\d100.raw"



def get_rssi(filename):
    df = pd.read_csv(filename,skiprows=23, sep=" ",names=["pos", "1", "2", "3","4","5"])
    del df["pos"]
    del df["5"]
    rssi_array=df.to_numpy().flatten()
    rssi=[int(rssi_array[i],16) for i in range(len(rssi_array))]
    return rssi

def main():

    rssi_05m=get_rssi(filename_05m)
    rssi_1m=get_rssi(filename_15m)
    rssi_15m=get_rssi(filename_15m)
    #rssi_iperf=get_rssi(filename_iperf)
    rssi_t0=get_rssi(filename_t0)
    rssi_t10=get_rssi(filename_t10)
    rssi_t20=get_rssi(filename_t20)
    rssi_t30=get_rssi(filename_t30)
    rssi_t40=get_rssi(filename_t40)
    rssi_t50=get_rssi(filename_t50)
    rssi_t60=get_rssi(filename_t60)
    rssi_t70=get_rssi(filename_t70)
    rssi_t80=get_rssi(filename_t80)
    rssi_t90=get_rssi(filename_t90)
    rssi_t100=get_rssi(filename_t100)
    print(rssi_t20)
    print(min(rssi_t10))
    print(min(rssi_t50))
    print(rssi_t50)
    
    
    fig = plt.figure()
    plt.plot(rssi_t0,label="RSSI center")
    plt.plot(rssi_t10,label="RSSI 10cm away")
    plt.plot(rssi_t20,label="RSSI 20cm away")
    plt.plot(rssi_t30,label="RSSI 30cm away")
    plt.plot(rssi_t40,label="RSSI 40cm away")
    plt.plot(rssi_t50,label="RSSI 50cm away")
    plt.plot(rssi_t60,label="RSSI 60cm away")
    plt.plot(rssi_t70,label="RSSI 70cm away")
    plt.plot(rssi_t80,label="RSSI 80cm away")
    plt.plot(rssi_t90,label="RSSI 90cm away")
    plt.plot(rssi_t100,label="RSSI 100cm away")

    plt.legend()
    plt.grid()
    plt.xlabel("#intruction")
    plt.ylabel("RSSI level")

    fig.savefig("RSSI characteristic in horizontal handoverv3 deactlight.pdf")
    fig.savefig("RSSI characteristic in horizontal handoverv3 deactlight.png")



    #print(filename_t2)
    x=[0,10,20,30,40,50,60,70,80,90,100]


    t0=[max(rssi_t0), min(rssi_t0), statistics.stdev(rssi_t0)]
    t10=[max(rssi_t10), min(rssi_t10), statistics.stdev(rssi_t10)]
    t20=[max(rssi_t20), min(rssi_t20), statistics.stdev(rssi_t20)]
    t30=[max(rssi_t30), min(rssi_t30), statistics.stdev(rssi_t30)]
    t40=[max(rssi_t40), min(rssi_t40), statistics.stdev(rssi_t40)]
    t50=[max(rssi_t50), min(rssi_t50), statistics.stdev(rssi_t50)]
    t60=[max(rssi_t60), min(rssi_t60), statistics.stdev(rssi_t60)]
    t70=[max(rssi_t70), min(rssi_t70), statistics.stdev(rssi_t70)]
    t80=[max(rssi_t80), min(rssi_t80), statistics.stdev(rssi_t80)]
    t90=[max(rssi_t90), min(rssi_t90), statistics.stdev(rssi_t90)]
    t100=[max(rssi_t100), min(rssi_t100), statistics.stdev(rssi_t100)]
    
    tmax=[max(rssi_t0),max(rssi_t10),max(rssi_t20),max(rssi_t30),max(rssi_t40),max(rssi_t50),max(rssi_t60),max(rssi_t70),max(rssi_t80),max(rssi_t90),max(rssi_t100)]
    tmin=[min(rssi_t0),min(rssi_t10),min(rssi_t20),min(rssi_t30),min(rssi_t40),min(rssi_t50),min(rssi_t60),min(rssi_t70),min(rssi_t80),min(rssi_t90),min(rssi_t100)]
    tdev=[statistics.stdev(rssi_t0),statistics.stdev(rssi_t10),statistics.stdev(rssi_t20),statistics.stdev(rssi_t30),statistics.stdev(rssi_t40),statistics.stdev(rssi_t50),statistics.stdev(rssi_t60),statistics.stdev(rssi_t70),statistics.stdev(rssi_t80),statistics.stdev(rssi_t90),statistics.stdev(rssi_t100)]

    tave=[statistics.mean(rssi_t0),statistics.mean(rssi_t10),statistics.mean(rssi_t20),statistics.mean(rssi_t30),statistics.mean(rssi_t40),statistics.mean(rssi_t50),statistics.mean(rssi_t60),statistics.mean(rssi_t70),statistics.mean(rssi_t80),statistics.mean(rssi_t90),statistics.mean(rssi_t100)]

    #print(tmax, tmin, tdev)
    print(statistics.mean(rssi_t50))
    fig = plt.figure()
       
    plt.plot(x,tmax,label="Max RSSI")
    plt.plot(x,tmin,label="Min RSSI")
    plt.plot(x,tdev,label="St.dev RSSI")
    plt.plot(x,tave,label="Mean RSSI")
   
    #print(t0)
    #plt.plot(rssi_iperf,label="IPERF")




    plt.legend()
    plt.grid()
    plt.xlabel("Distance from the center Tx1")
    plt.ylabel("RSSI level")
    #plt.xlim(0,2)
    fig.savefig("RSSI characteristic in horizontal handoverv3e deactlight ave 2023.pdf")
    fig.savefig("RSSI characteristic in horizontal handoverv3e deactlight ave 2023.png")
    plt.show()

    print("wait...")
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
