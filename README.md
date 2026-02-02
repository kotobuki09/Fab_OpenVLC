# Fab OpenVLC📡
## Intelligent Management System for OpenVLC 💡

The Intelligent Management System (IMS) is an innovative framework that seamlessly manages handovers in a hybrid system of Visible Light Communication (VLC) and WiFi. This repository provides comprehensive instructions for setting up and running the IMS on your testbed.

A demo of our IMS in action can be found on YouTube: [IMS Demo](https://www.youtube.com/watch?v=jDsohtGlPcM)

[![VideoIMS](https://i.imgur.com/rDzuBzk.png)](https://www.youtube.com/watch?v=jDsohtGlPcM "Hybrid Visible Light Communication/WiFi testbed")

Our testbed is built on the OpenVLC platform and uses the WiFi adapter TP-link TL-WN722N v2. The topology of the testbed is depicted below:

![Fab_032022](https://user-images.githubusercontent.com/34347264/157910137-6f7f791e-4902-4057-868a-5b31315243ff.png)

## 🛠️Installation Instructions🛠️

### 🕹️VLC Module🕹️

To create the VLC channel, please follow the instructions provided on the [OpenVLC Repository](https://github.com/openvlc/OpenVLC).

### 📶WiFi Module📶

For the WiFi channel, we have tested with different USB adapters. However, we encountered some issues with the TL-WN722N ver3 when integrating it into the testbed. If you have the same setup, you can refer to the [RTL8188EUS driver repository](https://github.com/aircrack-ng/rtl8188eus).

Here are the main instructions:

1. Install dependencies and change directory to /usr/src:

```bash
sudo apt-get install git dkms git make build-essential
cd /usr/src
```

2. Clone the repository:

```bash
sudo git clone https://github.com/abhijeet2096/TL-WN722N-V2
```

3. Add a symbolic link for dkms to know where the source is:

```bash
sudo dkms add ./TL-WN722N-V2
```

4. Build the source:

```bash
sudo dkms build -m 8188eu -v 1.2
```

5. Install the built drivers:

```bash
sudo dkms install -m 8188eu -v 1.2
```

6. Modprobe it:

```bash
sudo modprobe 8188eu
```

7. Reboot the system:

```bash
sudo reboot
```

Activating the monitor mode can provide more control over the WiFi network.

### 🧠IMS Module🧠

The Intelligent Management System (IMS) serves as the central controller, providing instructions to each OpenVLC in the network. Built on the Fabric framework, IMS can oversee and manage all activities of the VLC network from a single terminal. This makes it an invaluable tool for maintaining efficient and effective communication across your hybrid system.

Before running the demo, certain adjustments are necessary to ensure the Central Control Unit can gather information about the VLC and WiFi channels. This allows the controller to make informed decisions about when to perform handovers based on the quality of both channels.

## Setup Instructions

1. **File Transfer**: After completing all the WiFi-related setup, transfer the necessary files to both BBB-Tx (transmitter) and BBB-Rx (receiver). This will enable the IMS to operate effectively and manage both WiFi and VLC channels.

2. **Directory Setup**: If you change the directory, you might need to adjust the setup directory in the `fabfile.py` file as well to make the IMS work.

3. **Testbed Setup**: Modify the setup in `fabfile.py` to fit your testbed setup. Instructions are provided within the file.

4. **Configuration File**: Copy the `hostapd.conf` file from the `ControlUnit` folder to the `/etc/hostapd/` directory in BBB-Tx.

Please refer to the detailed instructions provided in the repository to configure your IMS setup properly. 

## 🚀Demo Activation🚀

![Topo](https://i.imgur.com/d7qZ2nL.jpeg)

### 🌐Creating a WiFi Network🌐

Navigate to the "ControlUnit" folder and open a terminal. Then, follow the instructions below to establish a WiFi and VLC network:
### 📶💡Activate BBB-Tx for WiFi and VLC channel📶💡
```bash
fab vlc1 setup_wifi_ap
fab vlc1 setup_vlc_tx
```
### 📶💡Activate BBB-Rx for WiFi and VLC channel📶💡
```bash
fab vlc2 setup_wifi_sta
fab vlc2 setup_vlc_rx
```
These commands will create a virtual interface in BBB, allowing for easier routing and traffic modifications, and enabling the devices to act as independent network connections.

### 🖧BBB-Tx-Virtual Interface 10:0 (Tx)🖧
```bash
sudo ip link add eth10 type dummy
sudo ifconfig eth10 hw ether 00:22:22:ff:ff:ff
sudo ip addr add 192.168.10.1/24 brd + dev eth10 label eth10:0
```
### 🖧BBB-Rx-Virtual Interface 10:0 (Rx)🖧
```bash
sudo ip link add eth10 type dummy
sudo ifconfig eth10 hw ether 00:22:22:ff:ff:f0
sudo ip addr add 192.168.10.2/24 brd + dev eth10 label eth10:0
```
### 📊Starting Iperf📊

Now you can create iperf traffic for testing with any experiment you're conducting by SSH through each BBB:

### 📥BBB-Tx📥
```bash
iperf -c 192.168.10.2 -u -b 1000M -l 800 -p 10001 -t 100000
```
### 📥BBB-Rx📥
```bash
iperf -u -l 800 -s -i3 -B 192.168.10.2 -p 10001
```
### 🎮Activate the controller IMS🎮
```bash
fab icontrol_demo
```
Now you can test how the handover work in your hybrid system.

### 🔄Forcing Handover🔄
Use the following commands to force a handover from the controller to a different link (either VLC or WiFi channel):

### 📶🟢Activate WiFi Link📶🟢
```bash
fab vlc1 wifi_link
```
### 💡🟢Activate VLC Link💡🟢
```bash
fab vlc1 vlc_link
```

### 📈RSSI Value Retrieval📈
To retrieve the RSSI value, use the following command:
```bash
sudo ./prubgb > filename.raw # Get the sample out
```

You can then use the provided Python script to visualize the RSSI output results.

<p float="center">
  <img src="https://i.imgur.com/3O79pXO.png" width="500" />
  <img src="https://i.imgur.com/Gv4ufDE.png" width="500" /> 
  <img src="https://i.imgur.com/gz8u2o0.png" width="500" />
</p>


## 📝Additional Notes📝

You can manually set up the system based on our code by referring to our `fabfile` controller or the `manual_IMS.txt` file located inside the ControlUnit folder.

### 📶📖Reading WiFi Channel Information📶📖

To read information from the WiFi channel, use the following command:

```bash
fab vlc2 wchannel
```

### 📊📖Reading Information from Iperf Application📊📖

To start the iperf server, use the following commands:

```bash
iperf -u -s -B 10.0.0.16 -p 10002
fab vlc1 iwifi
```

### 🧹🗄️Cleaning Log Files🧹🗄️

To delete all log files that are older than two days in BBB, use the following command:

```bash
find /var/log -mindepth 1 -mtime +2 -delete
```

## 📚Resources📚

Reference for this work:

- [A Novel Intelligent Management System Architecture](https://dl.acm.org/doi/10.1145/3570361.3615725)
- [Seamless Handover in Hybrid VLC and WiFi network](https://zenodo.org/records/7923924#.ZFyqyHZBxD8)

## 🐛Reporting Issues🐛

If you encounter any issues while using our system or have any suggestions for improvements, we encourage you to report them in the Issues section of this repository. 

We appreciate your help in improving our project. Your feedback is invaluable to us!

## 🙏Acknowledgments🙏 

**We'd like to thank everyone who has contributed to the these work!**  
We gratefully acknowledge support from:

- The [University of Palermo](https://www.unipa.it/)
- The [IMDEA Networks Institute](https://networks.imdea.org/)
- The [Toshiba Research Europe Ltd](https://www.toshiba.eu/pages/eu/Bristol-Research-and-Innovation-Laboratory/)

## 👤Personal Profile👤

For more information about the contributor, visit: [https://kngo.netlify.app/](https://kngo.netlify.app/)


