WiSHFUL RAS DEMO
============================

This demo example uses RAS antenna deployed on apu nodes in w-ilab2 testbed. The Reconfigurable Antenna Systems (RAS)
has been developed in the Open Call 1 extension of the WiSHFUL project by the ADANT company. The developed antennas are
capable of steering the radiation pattern dynamically on demand from typical omnidirectional to directional shape in
the azimuth plan.
This demo performs a network between to apu nodes and start a traffic stream between them. Afterwards the controller
changes the antenna directional configuration every 5 seconds and collect the measure of throughput and power in the apu
nodes. The demo validates how the antenna directional configuration improve the network performance in terms of
throughput and received power, and that is possible find a configuration better than the omnidirectional one.

DEMO START

 on not RAS station nodes
    sudo ./wishful_ras_agent --config agent_cfg.yaml

 on RAS station node
    sudo ./wishful_ras_agent --config  agent_ras_cfg.yaml

 on PC node
    ./wishful_ras_controller --config controller_cfg.yaml

NB: You can find in ./wishful_ras_controller program more details about nodes used in testbed and roles


## Acknowledgement

The research leading to these results has received funding from the European
Horizon 2020 Programme under grant agreement n645274 (WiSHFUL project).