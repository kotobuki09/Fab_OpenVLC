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

filename_idle="raw/dump_idle.raw"
filename_iperf="raw/dump_iperf_400K.raw"

filename_05m = "E:\\Fab_OpenVLC\\openVLC_RSSI_analyzer\\raw\\05m.raw"
filename_1m = "E:\\Fab_OpenVLC\\openVLC_RSSI_analyzer\\raw\\1m.raw"
filename_15m = "E:\\Fab_OpenVLC\\openVLC_RSSI_analyzer\\raw\\15m.raw"



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
    t1=np.array ([2038,10,871])
    t2=np.array ([1755, 316, 435])
    t3=np.array ([1327,742,206])

    t1=np.array ([2038,1755,1327])
    t2=np.array ([10,316,742])
    t3=np.array ([871,742,206])

    x = np.array([0.5, 1, 1.5])
    fig = plt.figure()

    plt.plot(x,t1,label="Max RSSI")
    plt.plot(x,t2,label="Min RSSI")
    plt.plot(x,t3,label="St.dev RSSI")

    #plt.plot(rssi_iperf,label="IPERF")

    plt.legend()
    plt.grid()
    plt.xlabel("Distance")
    plt.ylabel("RSSI level")
    #plt.xlim(0,2)
    fig.savefig("IDLE vs IPERF RSSI 3103.pdf")
    fig.savefig("IDLE vs IPERF RSSI 3103.png")
    plt.show()

    print("wait...")
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
