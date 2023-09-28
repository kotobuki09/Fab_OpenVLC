WiSHFUL WMP advanced tutorial
=============================

For any information or issue, please contact Domenico Garlisi at domenico.garlisi@cnit.it

The goal of this experiment is to create an advance example tutorial for the WiSHFUL framework and the UPI functions usage that
run on WMP platform. Specifically, this experiment uses the WiSHFUL framework and the UPI functions to set-up a wireless
WiFi network and change nodes radio program and parameters. All the UPI functions used in this example tutorial are fully
documented at link https://wishful-project.github.io/wishful_upis/ and this example tutorial can be found at the link
https://github.com/wishful-project/examples

In this showcase we demonstrate how learning mechanisms can be implemented in each node through the WiSHFUL framework, 
based on channel observations gathered by means of UPI functions. In particular, the general idea of the showcase is 
defining a medium access logic, which is not based on a pre-defined protocol (radio program in WiSHFUL), but rather 
is given by a combination of elementary protocols, which contribute to a final medium access decision by weighting 
opportunistically the decisions of each one. 
The basic idea of MAC learning has been introduced some years ago, in the so called Meta-MAC protocol [1]. 
In this Meta-MAC implementation, each protocol runs in parallel and takes a decision at each channel slot; the final 
medium access decision is obtained by choosing the protocol that optimize the node performance. At the end of the slot, 
protocols decisions are classified as or not correct in case they lead to successful transmissions, collisions or 
wasted channel time and their weights are updated accordingly. We exploit the formal definition of simple MAC protocol 
components and platform-independent representation of channel events gathered from the wireless node. This implementation
emulates the behavior of Meta-MAC by virtually executing multiple protocol components, learning about the performance 
of protocol components not running in the node, and dynamically reconfiguring the wireless nodes by loading the best 
expected protocol. 
For this advance example, we use five slotted radio program, a slotted p-persistence protocol with static retransmission 
probabilities p and four TDMA radio program that use different frame in super frame. 
In a slotted p-persistent protocol, whenever there is a packet queued, the probability of transmission in a slot is 
a constant p, independently for each slot. Thus, in each slot we decide to use one of these radio program. Conversely, 
TDMA protocols are characterized by the frame length and by the slot allocated to each node. For a given frame size, 
different allocations are mapped into different protocol components. Definitely, in this showcase we consider two type 
of slotted protocols, TDMA and p-persistence protocol; we also use channel feedback at the end of each slot, for 
updating the weight of each protocol as a function of its right/wrong decision. While for protocol simulation the channel 
feedback has to specify many different events (such as the reception of a specific frame), for estimating the correctness 
of the protocol decisions is generally enough to consider a ternary feedback (transmission occurred, collision occurred, 
or idle slot).

We want to demonstrate how the WISHFUL UPI can be exploited for:
i) Create a network topology with five nodes, an Access Point (AP) and four connected station (STA);
ii) Implement a control program that implements the meta-MAC algorithm in each node, updates the weights of the protocol 
components and loads the best protocol on each node; Collect low level channel measurements, in order to get a feedback 
at end of each time slot and classify protocol decisions are correct or incorrect; Tune radio program parameters; 
Switch from a radio program to another. 
iii) Deploy and run the local control program from controller node to the testbed nodes;

In order to implement the experiment, we run a controller program, or WiSHFUL controller, on a PC connected through
ethernet links to all nodes, and a common agent program in any node.
The controller program permits to: (i) discovery network nodes, (ii) install the execution environment, (iii) create the
BSS infrastructure and associate stations to the access point. In additional, the WiSHFUL controller executes the logic
for controlling the experiment, where we distinguish two phases: first deploy and run the control program on testbed nodes
second ....

The present example tutorial has been tested on WMP platform nodes present in the w-ilab.t. In order to better understand 
all the phases of the this example tutorial and the single UPI function usage, we add inline comment to both controller 
and control program.

For running this experiment, we use two different python scripts: the first script is responsible of network configuration, 
AP activation and station associations (metamac_testbed_controller); the second script is the most relevant one and 
implements the Global Control Program on top of the WiSHFUL global MCE (metamac_experiment_controller), which includes 
the metamac_local_control_program that is sent to the local controller of each node.

Below, you can find a step by step how-to to run this example in w-ilab.t by using five tesbed nodes, five alix stations
(alixnode8, alixnode9, alixnode10, alixnode11, alixnode12) where we will run the WiSHFUL agent, and a server to controll
them (an SERVER5P) where we will run the WiSHFUL controller. In order to setup the testbed and move all relevant files 
on nodes, the experiment directory contains four additional directory to collect different data, programs and bash scripts
able to provide more functionality to the user
    1) wmp_helper : contains functions to perform node configuration and data showcase analysis, specially the script
     sync_date.sh performs the time syncronization of the network nodes and the script deploy_upis.sh performs the files 
     synchronization;
    2) visualizer : contains a python GUI to control the experiment in terms of traffic enable/disable and selection of 
     a specific radio program for each nodes, alternatively the user can selects the Meta-MAC algorithm that automatically
     find the best radio program according with the traffic level (low / high);
    3) showcase_data : contains a burst of data result from an experiment and 2 python program to analyze and plot them;
    4) channel : contains a burst of data result with the full information for each slot in terms of slot statistics and 
     selected radio program;
     
### Experiment nodes selection and interface configuration
The file testbed_nodes.csv has been used to set the experiment nodes and the relative information information. For each node 
is needed reporting ip, hostname, role and platform. How reported below 

ip,hostname,role,platform,traffic
172.16.0.8,alix08,AP,wmp,0
172.16.0.9,alix09,STA,wmp,0
172.16.0.10,alix10,STA,wmp,0
172.16.0.12,alix12,STA,wmp,0
172.16.0.13,alix13,STA,wmp,0

### WORKING ON w-ilab.t with EMULAB

### 1. Reserve and run swap in experiment in w-ilab.t
Reserve all the ALIX nodes and two SERVER (SERVER3 and SERVER13), the USRP4 by the reservation system at : https://www.wilab2.ilabt.iminds.be/reservation/index.php/
Swap in the experiment alix-wishful present at : https://www.wilab2.ilabt.iminds.be/showexp.php3?pid=cognitiveradio&eid=alix-wishful

### 2. Get the experiment code, deploy it on nodes, and run the WiSHFUL controller on SERVER3
    SHELL 1 - WiSHFUL CONTROLLER :
        connect to controller PC [from ops.wilab2.ilabt.iminds.be]
            ssh alixserver.alix-wishful.cognitiveradio.wilab2.ilabt.iminds.be

        run command to set speed alixnode network
            sudo ethtool -s eth4 speed 100 duplex full

        clone on your directory the WiSHFUL project repository:
             follow the user installation How To present at link: https://github.com/wishful-project/manifests

        move in the experiment directory
                cd examples/Get_Started_Examples/Advanced-WPM-Examplel
 
            cd wmp_helper
        deploy framework on alixnodes
            sh deploy_upis.sh alixnode8,alixnode9,alixnode10,alixnode12,alixnode13

        sync nodes time:
            sh sync_date.sh alixnode8,alixnode9,alixnode10,alixnode12,alixnode13
            cd ..

### 3. Connect on ALIX agent nodes and run the WiSHFUL agent
    SHELL 2  - ALIXNODE8 (alix node password  : 123456) :
        connect to controller PC [from ops.wilab2.ilabt.iminds.be]
            ssh alixserver.alix-wishful.cognitiveradio.wilab2.ilabt.iminds.be

        connect to the ALIXNODE8
            ssh root@alixnode8

        move on the experiment directory
            cd wishful-github-manifest/examples/Get_Started_Examples/Advanced-WPM-Example

        start agent
            chmod +x metamac_agent
            python3 metamac_agent --config agent_config_ap.yaml (#run with -v for debugging)

    
    SHELL 3  - ALIXNODE9 (alix node password  : 123456) :
        connect to controller PC [from ops.wilab2.ilabt.iminds.be]
            ssh alixserver.alix-wishful.cognitiveradio.wilab2.ilabt.iminds.be

        connect to the ALIXNODE9
            ssh root@alixnode9

        move on the experiment directory
            cd wishful-github-manifest/examples/Get_Started_Examples/Simple-WPM-Example

        start agent
            chmod +x metamac_agent
            python3 metamac_agent --config agent_config.yaml (#run with -v for debugging)

    REPLACE THE SAME STEPS OF THE SHELL 3 FOR SHELL 4 (WITH ALIXNODE10), SHELL 5 (WITH ALIXNODE12), SHELL6 (WITH ALIXNODE13) 

### 4. Start controller on SERVER3
    python3 metamac_testbed_controller --config controller_config_wilab.yaml
    python3 metamac_experiment_controller --config controller_config_wilab.yaml (sudo apt-get install python3-matplotlib)

### 5. START USRP acquiring on SERVER13
    run_usrp.sh 6

### 6. START DEMO GUI VISUALIZER (on local pc) 
    forward command for experiment GUI visualizer
        ssh -L 8401:server3:8401 dgarlisi@ops.wilab2.ilabt.iminds.be -v (different shell)
        ssh -L 8400:server3:8400 dgarlisi@ops.wilab2.ilabt.iminds.be -v (different shell)
        ssh -L 8410:server13:80 dgarlisi@ops.wilab2.ilabt.iminds.be -v (different shell)

    test the USRP
        http://127.0.0.1:8410/crewdemo/plots/usrp.png
    
    run GUI visualize
        cd visualizer
        python metamac_visualizer.py 
    
### TO CONNECT THE ALIXNODE TO INTERNET
    #on alixnode
        sudo ip route add default via 172.16.0.100 dev eth0
        add nameserver 8.8.8.8 on resolv.conf
    #on alix server
        sudo /sbin/iptables -P FORWARD ACCEPT
        sudo /sbin/iptables --table nat -A POSTROUTING -o eth0 -j MASQUERADE

## Acknowledgement
The research leading to these results has received funding from the European
Horizon 2020 Programme under grant agreement n645274 (WiSHFUL project).

## REFERENCE
[1]Faragó, A. D. Myers, V. R. Syrotiuk, and G. Záruba, “Meta-MAC protocols: Automatic combination of MAC protocols to optimize performance for unknown conditions,” IEEE Journal on Selected Areas in Communications, vol. 18, no. 9, pp. 1670–1681, September 2000.