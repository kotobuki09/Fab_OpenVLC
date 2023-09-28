# Simple USRP spectrum sensor

Based on GNU Radio FFT and specviz.

## Running

```fish
while true; python2 gr-specmon/usrp_pwr_fft.py; sleep 0.4; end
```

Works best with bokeh based plotting ;)

## Installation

### Arch based host

```
sudo pacman -S gnuradio python2-pyzmq
sudo /usr/lib/uhd/utils/uhd_images_downloader.py
```

### Volk

To improve volk performance run:

```
volk_profile
```

### Other (currently outdated)

You need to install [GNU Radio](https://wiki.gnuradio.org/index.php/InstallingGR) and all the packages from `Pipfile` and `pyzmq`.

GNU Radio uses Python 2, however this code should be compatible with both Python 3 and 2.

## USRP setup

Test USRP by using:

```
uhd_usrp_probe
```

### N210

Set device address to `"addr=%s" % usrp_addr` for networked USRP.

Set bigger memory buffers:

```
sudo sysctl -w net.core.wmem_max=1048576
sudo sysctl -w net.core.rmem_max=50000000
```

and bigger mtu (unless setup in `NetworkManager`):

```
iw link set eth0 mtu 9000
```

On Lenovo L430 I was experiencing problems with ethernet after suspend. To reboot use:

```bash
sudo rmmod r8169
sudo modprobe r8169
```

### B205mini

Set device address to `"type=b200"` for USB based B205mini.

To get better performance you can try to add following to `/etc/security/limits.conf`.

```
@wheel           -       rtprio          50
```

Make sure you are member of `wheel` group.

# Other

```
sudo cp ~/final_showcase/webui/services/* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl status specmon-low specmon-high webui
```
