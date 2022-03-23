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
filename_idle_0_5 = "raw/test2.raw"
filename_iperf_0_5 = "raw/outbox_0_5m_iperf_nlos.raw"

filename_idle_1 = "raw/outbox_1m_idle_nlos.raw"
filename_iperf_1 = "raw/outbox_1m_iperf_nlos.raw"

filename_idle_1_5 = "raw/outbox_1_5m_idle_nlos.raw"
filename_iperf_1_5 = "raw/outbox_1_5m_iperf_nlos.raw"

def get_rssi(filename):
    df = pd.read_csv(filename,skiprows=23, sep=" ",names=["pos", "1", "2", "3","4","5"])
    del df["pos"]
    del df["5"]
    rssi_array=df.to_numpy().flatten()
    rssi=[int(rssi_array[i],16) for i in range(len(rssi_array))]
    return rssi
def main():

    rssi_idle_0_5=get_rssi(filename_idle_0_5)
    rssi_iperf_0_5=get_rssi(filename_iperf_0_5)

    rssi_idle_1=get_rssi(filename_idle_1)
    rssi_iperf_1=get_rssi(filename_iperf_1)

    rssi_idle_1_5=get_rssi(filename_idle_1_5)
    rssi_iperf_1_5=get_rssi(filename_iperf_1_5)
    fig = plt.figure()
    # Initialise the subplot function using number of rows and columns
    #figure, axis = plt.subplots(2, 2)

    plt.plot(rssi_idle_0_5[1:-1],label="IPERF test1")
    #plt.plot(rssi_iperf_0_5[1:-1],label="IPERF 0.5")

    #plt.plot(rssi_idle_1[1:-1],label="IDLE 1")
    #plt.plot(rssi_iperf_1[1:-1],label="IPERF 1")

    #plt.plot(rssi_idle_1_5[1:-1],label="IDLE 1.5")
    #plt.plot(rssi_iperf_1_5[1:-1],label="IPERF 1.5")




    plt.legend()
    plt.grid()
    plt.xlabel("#instruction event")
    plt.ylabel("RSSI level")
    plt.xlim(0,300)
    #plt.ylim(800,1200)
    fig.savefig("IDLE vs IPERF RSSI TEST2.pdf")
    fig.savefig("IDLE vs IPERF RSSI TEST2.png")
    plt.show()

    print("wait...")
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
