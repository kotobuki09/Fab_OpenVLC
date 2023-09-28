WiSHFUL WMP example tutorial
============================

For any information or issue, please contact Domenico Garlisi at domenico.garlisi@cnit.it

The goal of this experiment is to create an example tutorial for the WiSHFUL framework and the UPI functions usage that
run on WMP platform. Specifically, this experiment uses the WiSHFUL framework and the UPI functions to set-up a wireless
WiFi network and change nodes radio program and parameters. All the UPI functions used in this example tutorial are fully
documented at link https://wishful-project.github.io/wishful_upis/ and this example tutorial can be found at the link
https://github.com/wishful-project/examples

We want to demonstrate how the WISHFUL UPI can be exploited for:
i) Create a network topology with two nodes, an Access Point (AP) and a connected station (STA);
ii) Show how use the UPI functions to tune the nodes parameters;
iii) Switch from a carrier sense multiple access (CSMA) to a time-division access protocol(TDMA);

In order to implement the experiment, we run a controller program, or WiSHFUL controller, on a PC connected through
ethernet links to all nodes, and a common agent program in any node.
The controller program permits to: (i) discovery network nodes, (ii) install the execution environment, (iii) create the
BSS infrastructure and associate stations to the access point. In additional, the WiSHFUL controller executes the logic
for controlling the experiment, where we distinguish two phases: first tuning parameters of the node wireless interface
and radio program, second switching between CSMA radio programs (enabled by default) and TDMA radio program.

The present example tutorial has been tested on WMP platform nodes present in the w-ilab.t.

In order to better understand all the phases of the this example tutorial and the single UPI function usage, we add
inline comment to both controller and agent programs.

Below, you can find a step by step howto to run this example in w-ilab.t by using 3 tesbed nodes, two alix stations
(alixnode9 and alixnode12) where we will run the WiSHFUL agent, and a server to controll them (an SERVER5P) where we
will run the WiSHFUL controller. In order to setup the testbed and move all relevant files on nodes, the experiment
contains two bash script: 1)  sync_date.sh that performs the time syncronization of the network nodes; 2)  deploy_upis.sh
that performs the files syncronization


This example tutorial is composed of two main python programs and other 3 additional script and configuration files.
The python programs are i) wishful_example_tutorial_agent that runs the agent in the experiment nodes, and
ii) wishful_example_tutorial_controller that runs on experiment PC and performs experiment actions.

### Experiment nodes selection and interface configuration
Both, wishful_example_tutorial_controller and wishful_example_tutorial_agent contains a setting part, that must been
setted with the experiment nodes and PC information. For each node is needed reporting ip, name and interface.
An example of configuration is reported below.

"""
Setting of experiment nodes, ip address and name
"""
#PC
controller_PC_ip_address = "172.16.0.100"
controller_PC_interface = "eth4"

# AP
ap_name = "node0"
ap_ip = "172.16.0.9"
ap_wlan_interface = "wlan0"

# STA
sta_name = "node1"
sta_ip = "172.16.0.12"
sta_wlan_interface = "wlan0"

#Nodes number
nodes_number=2

# BSSID of our Network
network_bssid = "wishful_example_tutorial"
group_name = "example_tutorial"

"""
END setting of experiment nodes
"""

### 0. Experiment nodes on w-ilab.t
ALIX9       --> (node type ALIX)
ALIX12      --> (node type ALIX)
SERVER3     --> (node type SERVER5P)

### 1. Reserve and run swap in experiment in w-ilab.t
Reserve the experiment nodes by the reservation system at : https://www.wilab2.ilabt.iminds.be/reservation/index.php/
Use the NS file present in this directory example (wishful_wmp_example_wilabt.ns) to begin a testbed experiment at :
https://www.wilab2.ilabt.iminds.be/beginexp.php

Alternatively you can reserve all the ALIX nodes, two SERVER (SERVER3 and SERVER13), the USRP4 and swap in the
experiment alix-wishful at : https://www.wilab2.ilabt.iminds.be/showexp.php3?pid=cognitiveradio&eid=alix-wishful

### 2. Get the experiment code, deploy it on nodes, and run the WiSHFUL controller
    SHELL 1 - WiSHFUL CONTROLLER :
        connect to controller PC [from ops.wilab2.ilabt.iminds.be]
            ssh alixserver.alix-wishful.cognitiveradio.wilab2.ilabt.iminds.be

        run command to set speed alixnode network
            sudo ethtool -s eth4 speed 100 duplex full

        clone on your directory the WiSHFUL project repository:
             follow the user installation How To present at link: https://github.com/wishful-project/manifests

        move in the experiment directory
                cd examples/Get_Started_Examples/Simple-WPM-Example

        deploy framework on alixnodes
            sh deploy_upis.sh alixnode9,alixnode12

        sync nodes time:
            sh sync_date.sh alixnode9,alixnode12

        start controller
            chmod +x wmp_example_tutorial_controller
            ./wmp_example_tutorial_controller (#run with -v for debugging)


### 3. Connect on ALIX agent nodes and run the WiSHFUL agent
    SHELL 2  - ALIXNODE9 (alix node password  : 123456) :
        connect to controller PC [from ops.wilab2.ilabt.iminds.be]
            ssh alixserver.alix-wishful.cognitiveradio.wilab2.ilabt.iminds.be

        connect to the ALIXNODE9
            ssh root@alixnode9

        move on the experiment directory
            cd wishful-github-manifest/examples/Get_Started_Examples/Simple-WPM-Example

        start agent
            chmod +x wmp_example_tutorial_agent
            ./wmp_example_tutorial_agent (#run with -v for debugging)

    SHELL 3 - ALIXNODE12 (alix node password  : 123456) :
        connect to controller PC [from ops.wilab2.ilabt.iminds.be]
            ssh alixserver.alix-wishful.cognitiveradio.wilab2.ilabt.iminds.be

        connect to the ALIXNODE12
            ssh root@alixnode12

        move on the experiment directory
            cd wishful-github-manifest/examples/Get_Started_Examples/Simple-WPM-Example

        start agent
            chmod +x wmp_example_tutorial_agent
            ./wmp_example_tutorial_agent (#run with -v for debugging)


## Acknowledgement
The research leading to these results has received funding from the European
Horizon 2020 Programme under grant agreement n645274 (WiSHFUL project).
