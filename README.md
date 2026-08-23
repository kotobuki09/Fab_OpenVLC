<div align="center">

# Fab OpenVLC

### Intelligent handover management for hybrid Visible Light Communication and Wi-Fi testbeds

[![Project status](https://img.shields.io/badge/status-research%20prototype-6f42c1?style=flat-square)](#project-status)
[![GitHub stars](https://img.shields.io/github/stars/kotobuki09/Fab_OpenVLC?style=flat-square)](https://github.com/kotobuki09/Fab_OpenVLC/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/kotobuki09/Fab_OpenVLC?style=flat-square)](https://github.com/kotobuki09/Fab_OpenVLC/forks)
[![Open issues](https://img.shields.io/github/issues/kotobuki09/Fab_OpenVLC?style=flat-square)](https://github.com/kotobuki09/Fab_OpenVLC/issues)
[![Last commit](https://img.shields.io/github/last-commit/kotobuki09/Fab_OpenVLC?style=flat-square)](https://github.com/kotobuki09/Fab_OpenVLC/commits/main)

**Fab OpenVLC** is an experimental research framework for monitoring, controlling, and evaluating handovers between **Visible Light Communication (VLC)** and **Wi-Fi** links. It combines OpenVLC, BeagleBone Black devices, traffic generation, channel measurements, and a Fabric-based Intelligent Management System in a reproducible hybrid-network testbed.

[Demo](https://www.youtube.com/watch?v=jDsohtGlPcM) · [Installation](#installation-and-configuration) · [Run an experiment](#running-the-testbed) · [Contribute](CONTRIBUTING.md) · [Roadmap](ROADMAP.md) · [Cite](CITATION.cff)

</div>

---

## Overview

Hybrid VLC/Wi-Fi systems combine complementary communication technologies:

- **VLC** offers high spatial reuse, directional communication, and operation in environments where radio-frequency interference is undesirable.
- **Wi-Fi** provides wider coverage, mobility support, and a robust fallback when the optical link is blocked or degraded.

The central research challenge is deciding **when and how to switch between these links without unnecessarily interrupting application traffic**. Fab OpenVLC provides an Intelligent Management System (IMS) that collects link information, controls the transmitter and receiver, and coordinates handover experiments from a central terminal.

The repository is intended for researchers, students, and engineers working on:

- visible-light communication and LiFi;
- hybrid optical/radio networks;
- mobility and handover management;
- experimental networking and testbed automation;
- channel-quality monitoring;
- reproducible wireless-system evaluation.

## Why this project matters

Evaluating hybrid VLC/Wi-Fi networks normally requires researchers to integrate several independent components: optical hardware, wireless adapters, Linux networking, traffic generators, measurement tools, remote-control scripts, and handover logic. Rebuilding that environment from scratch is time-consuming and can make results difficult to reproduce across laboratories.

Fab OpenVLC reduces that burden by providing:

- a documented hybrid VLC/Wi-Fi topology;
- centralized testbed control through Fabric tasks;
- transmitter and receiver configurations for BeagleBone Black devices;
- procedures for creating VLC and Wi-Fi links;
- traffic generation with `iperf`;
- manual and controller-driven link switching;
- RSSI and channel-information collection;
- plotting utilities for experimental measurements;
- contribution and citation infrastructure for continued research use.

## Key capabilities

| Capability | Description |
|---|---|
| Centralized management | Operate the hybrid testbed from the `ControlUnit` host. |
| Link setup | Configure VLC and Wi-Fi transmitter/receiver roles remotely. |
| Handover control | Run the IMS controller or force traffic onto a selected link. |
| Traffic generation | Generate repeatable UDP traffic using `iperf`. |
| Channel monitoring | Retrieve Wi-Fi and VLC-related measurements for decision-making. |
| RSSI capture | Export raw measurement samples for subsequent analysis. |
| Experiment visualization | Use the scripts under `PlotGraph/` to visualize collected data. |
| Reproducibility support | Record configurations, measurements, code revisions, and experiment conditions. |

## System architecture

The testbed contains three logical control points:

| Component | Role |
|---|---|
| **Control Unit** | Runs Fabric tasks, collects measurements, and executes the IMS handover logic. |
| **BBB-Tx** | BeagleBone Black transmitter providing the VLC transmitter and Wi-Fi access-point functions. |
| **BBB-Rx** | BeagleBone Black receiver providing the VLC receiver and Wi-Fi station functions. |

Traffic can be carried over either the VLC link or the Wi-Fi link. Virtual interfaces are used to simplify routing and allow the two physical links to be treated as independent network paths.

![Fab OpenVLC testbed topology](https://user-images.githubusercontent.com/34347264/157910137-6f7f791e-4902-4057-868a-5b31315243ff.png)

### Demonstration

[![Fab OpenVLC IMS demonstration](https://i.imgur.com/rDzuBzk.png)](https://www.youtube.com/watch?v=jDsohtGlPcM "Hybrid VLC/Wi-Fi testbed demonstration")

## Repository structure

```text
Fab_OpenVLC/
├── ControlUnit/          # Fabric controller, IMS logic, and control configuration
├── BBB_Tx_Full_Repo/     # Transmitter-side software and dependencies
├── BBB_Rx_Full_Repo/     # Receiver-side software and dependencies
├── PlotGraph/            # Measurement visualization scripts
├── prudebug-bbb/         # PRU debugging and sample-capture utilities
├── images/               # Repository images and author assets
├── CONTRIBUTING.md       # Contribution workflow and reproducibility guidance
├── ROADMAP.md            # Planned engineering and research improvements
├── CITATION.cff          # Machine-readable software citation metadata
└── README.md
```

> The transmitter and receiver directories include complete experimental working environments and third-party components. Review the relevant license files before reuse or redistribution.

## Hardware and software requirements

### Hardware

- two BeagleBone Black devices, used as **BBB-Tx** and **BBB-Rx**;
- an OpenVLC-compatible transmitter and receiver setup;
- Wi-Fi adapters for the hybrid radio link;
- a Linux computer used as the Control Unit;
- Ethernet or another management network providing SSH access to both BeagleBone devices.

### Tested Wi-Fi hardware

The original testbed was developed using the **TP-Link TL-WN722N v2**. Other adapters may work, but driver, monitor-mode, and `hostapd` compatibility must be verified independently.

The TL-WN722N v3 was reported to present integration difficulties in the original setup. Record the exact adapter model and hardware revision when reporting results or issues.

### Software

- Linux on the Control Unit and BeagleBone Black devices;
- OpenVLC, following the upstream [OpenVLC repository](https://github.com/openvlc/OpenVLC);
- Python and a Fabric release compatible with `ControlUnit/fabfile.py`;
- SSH access from the Control Unit to both BeagleBone devices;
- `iperf` for UDP traffic generation;
- `hostapd` for the Wi-Fi access point;
- DKMS and build tools when an external Wi-Fi driver is required;
- Python plotting dependencies required by the scripts under `PlotGraph/`.

> The repository uses the classic `fab <host> <task>` command style. Verify the Fabric version and Python environment before running controller tasks.

## Installation and configuration

### 1. Clone the repository

```bash
git clone https://github.com/kotobuki09/Fab_OpenVLC.git
cd Fab_OpenVLC
```

### 2. Configure OpenVLC

Install and validate the VLC channel on both BeagleBone devices using the instructions in the upstream [OpenVLC repository](https://github.com/openvlc/OpenVLC).

Before integrating the IMS, confirm that:

- the transmitter can send data over the VLC link;
- the receiver can receive that data;
- both devices are reachable from the Control Unit over SSH;
- the OpenVLC paths used by the controller match the paths on each device.

### 3. Configure the Wi-Fi adapter

Use a driver supported by your adapter and Linux kernel. The original testbed used an `8188eu`-based workflow for the TL-WN722N v2.

<details>
<summary><strong>Legacy TL-WN722N v2 driver workflow used by the original testbed</strong></summary>

```bash
sudo apt-get update
sudo apt-get install -y git dkms make build-essential
cd /usr/src
sudo git clone https://github.com/abhijeet2096/TL-WN722N-V2
sudo dkms add ./TL-WN722N-V2
sudo dkms build -m 8188eu -v 1.2
sudo dkms install -m 8188eu -v 1.2
sudo modprobe 8188eu
sudo reboot
```

This procedure is retained for reproducibility of the original environment. Kernel and driver compatibility may differ on current systems. Validate the upstream driver source before installation.

</details>

### 4. Configure the Control Unit

Open `ControlUnit/fabfile.py` and adapt the environment to your testbed. At minimum, verify:

- BBB-Tx and BBB-Rx IP addresses;
- SSH usernames, authentication, and ports;
- local and remote working directories;
- interface names;
- VLC and Wi-Fi configuration paths;
- traffic-generation addresses and ports;
- any threshold or timing values used by the IMS.

Avoid committing passwords, private keys, or institution-specific credentials to the repository.

### 5. Configure `hostapd`

Copy the testbed `hostapd.conf` configuration from the Control Unit resources to BBB-Tx:

```bash
sudo cp hostapd.conf /etc/hostapd/hostapd.conf
```

Review the interface name, SSID, channel, country code, and security settings before starting the access point.

### 6. Transfer required files

Transfer the relevant transmitter-side resources to BBB-Tx and receiver-side resources to BBB-Rx. If the destination directories differ from the original testbed, update the paths in `ControlUnit/fabfile.py` accordingly.

## Running the testbed

Run the following commands from the `ControlUnit/` directory unless stated otherwise.

```bash
cd ControlUnit
```

### 1. Start BBB-Tx

Configure the Wi-Fi access point and VLC transmitter:

```bash
fab vlc1 setup_wifi_ap
fab vlc1 setup_vlc_tx
```

### 2. Start BBB-Rx

Configure the Wi-Fi station and VLC receiver:

```bash
fab vlc2 setup_wifi_sta
fab vlc2 setup_vlc_rx
```

### 3. Create virtual interfaces

The following commands reproduce the virtual-interface configuration used by the original testbed.

#### BBB-Tx

```bash
sudo ip link add eth10 type dummy
sudo ifconfig eth10 hw ether 00:22:22:ff:ff:ff
sudo ip addr add 192.168.10.1/24 brd + dev eth10 label eth10:0
```

#### BBB-Rx

```bash
sudo ip link add eth10 type dummy
sudo ifconfig eth10 hw ether 00:22:22:ff:ff:f0
sudo ip addr add 192.168.10.2/24 brd + dev eth10 label eth10:0
```

These addresses are testbed defaults. Change them if they conflict with your network. Some modern distributions do not install `ifconfig` by default; use an equivalent `ip link` command or install the required networking tools.

### 4. Start UDP traffic

Start the server on BBB-Rx:

```bash
iperf -u -l 800 -s -i 3 -B 192.168.10.2 -p 10001
```

Start the client on BBB-Tx:

```bash
iperf -c 192.168.10.2 -u -b 1000M -l 800 -p 10001 -t 100000
```

The values above reproduce the original experimental command. Select a realistic offered load for your link capacity and document every traffic parameter used in published results.

### 5. Start the IMS controller

```bash
fab icontrol_demo
```

The controller gathers channel information and applies the configured handover logic. Confirm that both nodes are reachable and that the expected measurement commands work before starting a long experiment.

## Manual link selection

Use the following commands to force traffic onto a specific link during testing.

### Select Wi-Fi

```bash
fab vlc1 wifi_link
```

### Select VLC

```bash
fab vlc1 vlc_link
```

Manual selection is useful for validating routing, establishing baseline performance, and comparing forced-link results with controller-driven handovers.

## Measurements and visualization

### Read Wi-Fi channel information

```bash
fab vlc2 wchannel
```

### Read application traffic information

Start an `iperf` server for the configured measurement path:

```bash
iperf -u -s -B 10.0.0.16 -p 10002
```

Then collect the corresponding information from the controller:

```bash
fab vlc1 iwifi
```

Update the bind address and port to match your environment.

### Capture RSSI samples

On the relevant BeagleBone device:

```bash
sudo ./prubgb > filename.raw
```

Store the following metadata with each capture:

- date and time;
- repository commit hash;
- transmitter/receiver geometry;
- optical and radio configuration;
- hardware and driver revisions;
- traffic parameters;
- sampling duration;
- units and preprocessing steps.

Use the utilities under `PlotGraph/` to inspect and visualize the recorded samples.

<p align="center">
  <img src="https://i.imgur.com/3O79pXO.png" width="31%" alt="Fab OpenVLC measurement example 1">
  <img src="https://i.imgur.com/Gv4ufDE.png" width="31%" alt="Fab OpenVLC measurement example 2">
  <img src="https://i.imgur.com/gz8u2o0.png" width="31%" alt="Fab OpenVLC measurement example 3">
</p>

## Experimental reproducibility

For every experiment, report at least:

1. the exact Fab OpenVLC commit or release;
2. BeagleBone Black revisions and operating-system images;
3. Linux kernel, OpenVLC, driver, Fabric, `hostapd`, and `iperf` versions;
4. Wi-Fi adapter model and hardware revision;
5. room geometry, transmitter-receiver distance, orientation, and lighting conditions;
6. IP addresses, interfaces, routes, and traffic parameters;
7. handover thresholds and decision intervals;
8. number of trials and trial duration;
9. definitions of handover latency, interruption time, packet loss, throughput, and jitter;
10. raw data, processing scripts, and figure-generation commands.

Do not delete broad system-log directories as part of an experiment. Keep project logs in a dedicated directory and clean only that location, for example:

```bash
find ./experiment-logs -type f -mtime +2 -delete
```

## Project status

Fab OpenVLC is a **research prototype**, not a production networking product. It is hardware-dependent and may require adaptation for current kernels, drivers, network interfaces, and OpenVLC versions.

Public adoption is represented by the live GitHub badges at the top of this page, together with forks, issues, pull requests, citations, and independently reproduced experiments. Package-registry monthly download statistics are not applicable because this project is not distributed through npm, PyPI, Maven, or a comparable package registry.

Current improvement priorities are documented in [ROADMAP.md](ROADMAP.md). Beginner and research contribution opportunities are available in the [issue tracker](https://github.com/kotobuki09/Fab_OpenVLC/issues).

## Known limitations

- The current setup is closely tied to a specific experimental hardware configuration.
- Paths, addresses, interfaces, and credentials must be reviewed before execution.
- External Wi-Fi drivers may not support every current Linux kernel.
- Hardware-dependent behavior cannot be fully validated through conventional cloud CI.
- The repository contains complete working environments and third-party components, which increases its size and licensing complexity.
- A fully automated clean installation and standardized compatibility matrix remain future work.

## Research outputs

This repository supports the following research artifacts:

- [A Novel Intelligent Management System Architecture](https://dl.acm.org/doi/10.1145/3570361.3615725)
- [Seamless Handover in Hybrid VLC and WiFi Network](https://zenodo.org/records/7923924)

## Citation

GitHub can generate a citation from [`CITATION.cff`](CITATION.cff). When using this repository in academic work:

- cite the software repository;
- cite the relevant publication or dataset above;
- record the exact commit or release used;
- describe any modifications made to the controller, hardware, or experiment configuration.

## Contributing

Contributions are welcome in the following areas:

- installation and compatibility documentation;
- setup automation;
- hardware support;
- measurement and plotting tools;
- handover algorithms;
- experiment reproducibility;
- tests, validation scripts, and safer configuration management.

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. For planned work, see [ROADMAP.md](ROADMAP.md). Use the structured [issue forms](https://github.com/kotobuki09/Fab_OpenVLC/issues/new/choose) for bug reports and research or feature proposals.

## Support and issue reporting

When reporting a problem, include:

- the failing command and complete error output;
- operating-system and kernel versions;
- hardware and Wi-Fi adapter revisions;
- OpenVLC, Fabric, driver, `hostapd`, and `iperf` versions;
- relevant changes made to `fabfile.py`;
- a minimal sequence that reproduces the issue;
- logs with credentials and private network information removed.

Open an issue through the [GitHub issue tracker](https://github.com/kotobuki09/Fab_OpenVLC/issues/new/choose).

## Acknowledgments

This work acknowledges support and collaboration from:

- [University of Palermo](https://www.unipa.it/)
- [IMDEA Networks Institute](https://networks.imdea.org/)
- [Toshiba Research Europe Ltd](https://www.toshiba.eu/pages/eu/Bristol-Research-and-Innovation-Laboratory/)
- the OpenVLC community and upstream open-source projects included in the experimental environment.

## Maintainer

**Ngô Trung Kiên**  
Hanoi School of Business and Management, Vietnam National University, Hanoi  
Faculty of Non-Traditional Security  
Website: [kngo.netlify.app](https://kngo.netlify.app/)  
Email: [kiennt@hsb.edu.vn](mailto:kiennt@hsb.edu.vn)

## Licensing and third-party software

This repository contains original research code together with third-party software, drivers, and utilities. Those components remain subject to their respective license notices. Review the license files in the relevant directories before modifying, redistributing, or incorporating the software into another project.

---

<div align="center">

If Fab OpenVLC supports your research or teaching, consider starring the repository and sharing a reproducible experiment or improvement.

</div>

## Sample RSSI dataset

- Data: [`data/sample_rssi.csv`](data/sample_rssi.csv)
- Plot: `python examples/plot_rssi.py`
