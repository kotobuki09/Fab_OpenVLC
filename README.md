# Fab OpenVLC 📡

## Intelligent Management System for Hybrid OpenVLC and WiFi Networks 💡

[![GitHub stars](https://img.shields.io/github/stars/kotobuki09/Fab_OpenVLC?style=for-the-badge)](https://github.com/kotobuki09/Fab_OpenVLC/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/kotobuki09/Fab_OpenVLC?style=for-the-badge)](https://github.com/kotobuki09/Fab_OpenVLC/forks)
[![Open issues](https://img.shields.io/github/issues/kotobuki09/Fab_OpenVLC?style=for-the-badge)](https://github.com/kotobuki09/Fab_OpenVLC/issues)
[![Last commit](https://img.shields.io/github/last-commit/kotobuki09/Fab_OpenVLC?style=for-the-badge)](https://github.com/kotobuki09/Fab_OpenVLC/commits/main)

Fab OpenVLC provides an experimental framework for monitoring and managing seamless handovers in hybrid **Visible Light Communication (VLC)** and **WiFi** networks. It combines OpenVLC, BeagleBone Black devices, WiFi channel monitoring, traffic generation, and a Fabric-based Intelligent Management System (IMS) in one reproducible research testbed.

> ⭐ If this repository supports your research, teaching, or experiments, please star it so that more VLC and hybrid-network researchers can discover it.

[Watch the IMS demo](https://www.youtube.com/watch?v=jDsohtGlPcM) · [Report a problem](https://github.com/kotobuki09/Fab_OpenVLC/issues/new/choose) · [Contribute](CONTRIBUTING.md) · [View the roadmap](ROADMAP.md) · [Cite this software](CITATION.cff)

## Why this project matters

Hybrid VLC/WiFi systems can combine the high spatial reuse and electromagnetic-interference resilience of optical links with the coverage and mobility support of radio networks. However, experimentally evaluating these systems requires coordinated hardware setup, channel measurements, traffic generation, link selection, and repeatable handover procedures.

Fab OpenVLC reduces that setup burden by providing:

- a working hybrid VLC/WiFi testbed architecture;
- centralized link monitoring and handover control;
- practical BeagleBone Black transmitter and receiver configurations;
- WiFi and VLC measurement and traffic-generation procedures;
- scripts and instructions that researchers can extend for new handover algorithms, measurements, and reproducibility studies.

The project is especially relevant to researchers and students working on visible-light communication, LiFi, hybrid networking, software-defined experimentation, mobility management, and future indoor wireless systems.

## Community and contributions

This is research software rather than a package published to npm or PyPI, so package-registry monthly download statistics are not applicable. GitHub stars, forks, issues, pull requests, citations, and reproduced experiments are the most meaningful public adoption signals for this project.

Contributions are welcome in documentation, setup automation, hardware compatibility, measurements, visualization, testing, and handover algorithms. Beginner-friendly tasks are published in the issue tracker. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## Demo

[![IMS demo](https://i.imgur.com/rDzuBzk.png)](https://www.youtube.com/watch?v=jDsohtGlPcM "Hybrid Visible Light Communication/WiFi testbed")

Our testbed is built on the [OpenVLC platform](https://github.com/openvlc/OpenVLC) and uses the TP-Link TL-WN722N v2 WiFi adapter.

![Fab OpenVLC testbed topology](https://user-images.githubusercontent.com/34347264/157910137-6f7f791e-4902-4057-868a-5b31315243ff.png)

## 🛠️ Installation Instructions

### 🕹️ VLC Module

To create the VLC channel, follow the instructions provided in the [OpenVLC repository](https://github.com/openvlc/OpenVLC).

### 📶 WiFi Module

We tested different USB WiFi adapters. We encountered integration issues with the TL-WN722N v3. For compatible RTL8188EUS-based setups, refer to the [RTL8188EUS driver repository](https://github.com/aircrack-ng/rtl8188eus).

Install the dependencies and change to `/usr/src`:

```bash
sudo apt-get install git dkms make build-essential
cd /usr/src
```

Clone the driver repository:

```bash
sudo git clone https://github.com/abhijeet2096/TL-WN722N-V2
```

Add, build, and install the DKMS module:

```bash
sudo dkms add ./TL-WN722N-V2
sudo dkms build -m 8188eu -v 1.2
sudo dkms install -m 8188eu -v 1.2
sudo modprobe 8188eu
sudo reboot
```

Monitor mode can provide additional control and channel-observation capabilities for experiments.

### 🧠 IMS Module

The Intelligent Management System is the central controller. Built with Fabric, it monitors the VLC and WiFi channels and instructs OpenVLC nodes when to change links. This enables experiments involving channel-aware handover decisions and centralized network management.

Before running the demo, configure the Central Control Unit so it can gather information about both channels.

## Setup Instructions

1. **File transfer:** Transfer the required files to both BBB-Tx and BBB-Rx after completing the WiFi setup.
2. **Directory setup:** If you change the installation directory, update the corresponding path in `fabfile.py`.
3. **Testbed setup:** Modify the hosts and parameters in `fabfile.py` to match your hardware.
4. **Access-point configuration:** Copy `ControlUnit/hostapd.conf` to `/etc/hostapd/` on BBB-Tx.

## 🚀 Demo Activation

![Demo topology](https://i.imgur.com/d7qZ2nL.jpeg)

### Create the WiFi and VLC network

From the `ControlUnit` directory, activate BBB-Tx:

```bash
fab vlc1 setup_wifi_ap
fab vlc1 setup_vlc_tx
```

Activate BBB-Rx:

```bash
fab vlc2 setup_wifi_sta
fab vlc2 setup_vlc_rx
```

These commands create virtual interfaces that simplify routing and allow the WiFi and VLC links to be managed independently.

### BBB-Tx virtual interface

```bash
sudo ip link add eth10 type dummy
sudo ifconfig eth10 hw ether 00:22:22:ff:ff:ff
sudo ip addr add 192.168.10.1/24 brd + dev eth10 label eth10:0
```

### BBB-Rx virtual interface

```bash
sudo ip link add eth10 type dummy
sudo ifconfig eth10 hw ether 00:22:22:ff:ff:f0
sudo ip addr add 192.168.10.2/24 brd + dev eth10 label eth10:0
```

### Generate traffic with iperf

On BBB-Tx:

```bash
iperf -c 192.168.10.2 -u -b 1000M -l 800 -p 10001 -t 100000
```

On BBB-Rx:

```bash
iperf -u -l 800 -s -i3 -B 192.168.10.2 -p 10001
```

### Start the IMS controller

```bash
fab icontrol_demo
```

You can now test handovers in the hybrid system.

### Force a handover

Activate the WiFi link:

```bash
fab vlc1 wifi_link
```

Activate the VLC link:

```bash
fab vlc1 vlc_link
```

### Retrieve RSSI samples

```bash
sudo ./prubgb > filename.raw
```

Use the provided Python script to visualize the resulting RSSI samples.

<p align="center">
  <img src="https://i.imgur.com/3O79pXO.png" width="31%" alt="RSSI result 1" />
  <img src="https://i.imgur.com/Gv4ufDE.png" width="31%" alt="RSSI result 2" />
  <img src="https://i.imgur.com/gz8u2o0.png" width="31%" alt="RSSI result 3" />
</p>

## 📝 Additional Commands

Manually configure the system by consulting the Fabric controller or `ControlUnit/manual_IMS.txt`.

Read WiFi channel information:

```bash
fab vlc2 wchannel
```

Start the iperf server and read application information:

```bash
iperf -u -s -B 10.0.0.16 -p 10002
fab vlc1 iwifi
```

Delete log files older than two days:

```bash
find /var/log -mindepth 1 -mtime +2 -delete
```

## 📚 Research Resources

- [A Novel Intelligent Management System Architecture](https://dl.acm.org/doi/10.1145/3570361.3615725)
- [Seamless Handover in Hybrid VLC and WiFi Network](https://zenodo.org/records/7923924)

Use the repository's [CITATION.cff](CITATION.cff) file when citing the software. GitHub also provides a **Cite this repository** option in the repository sidebar.

## 🐛 Reporting Issues

Use the structured [issue forms](https://github.com/kotobuki09/Fab_OpenVLC/issues/new/choose) to report reproducibility problems, hardware incompatibilities, bugs, or research-extension proposals. Include hardware versions, operating-system information, commands, logs, and expected behavior whenever possible.

## 🙏 Acknowledgments

We gratefully acknowledge support from:

- [University of Palermo](https://www.unipa.it/)
- [IMDEA Networks Institute](https://networks.imdea.org/)
- [Toshiba Research Europe Ltd](https://www.toshiba.eu/pages/eu/Bristol-Research-and-Innovation-Laboratory/)

## 👨‍💼 Author

<table>
  <tr>
    <td>
      <a href="https://kngo.netlify.app/">
        <img src="images/profile.png" alt="Ngo Trung Kien" width="120" />
      </a>
    </td>
    <td>
      <strong>NGÔ TRUNG KIÊN</strong><br />
      🌐 <a href="https://kngo.netlify.app/">kngo.netlify.app</a><br />
      📧 kiennt@hsb.edu.vn<br />
      🏫 Hanoi School of Business and Management (HSB)<br />
      Faculty of Non-Traditional Security
    </td>
  </tr>
</table>
