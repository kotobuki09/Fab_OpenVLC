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
import os


cwd = os.getcwd()
filename_idle="raw/outbox_0_5m_idle_nlos.raw"
filename_iperf="raw/outbox_0_5m_iperf_nlos.raw"

def get_rssi(filename):
    df = pd.read_csv(filename,skiprows=23, sep=" ",names=["pos", "1", "2", "3","4","5"])
    del df["pos"]
    del df["5"]
    rssi_array=df.to_numpy().flatten()
    rssi=[int(rssi_array[i],16) for i in range(len(rssi_array))]
    return rssi
def main():

    rssi_idle=get_rssi(filename_idle)
    #print(rssi_idle)
    rssi_iperf=get_rssi(filename_iperf)
    fig = plt.figure()
    plt.plot(rssi_idle,label="IDLE")
    plt.plot(rssi_iperf,label="IPERF")

    plt.legend()
    plt.grid()
    plt.xlabel("#instruction event")
    plt.ylabel("RSSI level")
    plt.xlim(0,300)
    fig.savefig("IDLE vs IPERF RSSI 0_5 NLOS.pdf")
    fig.savefig("IDLE vs IPERF RSSI 0_5 NLOS.png")
    plt.show()

    print("wait...")
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
