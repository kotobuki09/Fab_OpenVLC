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
