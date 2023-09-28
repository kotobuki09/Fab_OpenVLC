Wishful showcase 3 year 1 - Load and Interference aware MAC adaptation
============================

For any information or issue, please contact Domenico Garlisi at domenico.garlisi@cnit.it

It is well known that contention-based access protocols work better than scheduled-based protocols in case of intermittent and unpredictable traffic flows;
moreover, the contention parameters can be optimized as a function of the time-varying number of nodes which have traffic to transmit.
However, for most wireless technologies, the choice of contention-based or scheduled-based access protocols, as well as the configuration of
the contention parameters can only be change statically, and cannot be adapted to the varying network conditions.
We start from this consideration to implement an example of WiSHFUL controller in which we use the UPI function to understand the network loading and,
according with this value, set opportunistically one of the radio programs available and the their parameters.
In this exemplary experiment, we want to demonstrate how the WISHFUL UPI can be exploited for implementing two different control logic able to:
i) dynamically tune the contention parameters of contention-based protocols as a function of the load and interference conditions experienced in the network,
and ii) switch to a time-division access protocol in case of severe congestion levels.
We consider a network topology with a single contention domain (where all the nodes are visible) and an environment where other networks can be active.
In the following of this section, we refer to wireless devices used in the experiment (STA, AP) as nodes, whereas we use one PC, connected through ethernet
links to all nodes, to run the experiment controller and the WiSHFUL controller.

In this exemplary experiment we use two different programs, one is the experiment controller (showcase3_experiment_controller) and the other is the
WiSHFUL testbed controller (showcase3_testbed_controller). They permit to: (i) discovery network nodes, (ii) install the execution environment,
(iii) create the BSS infrastructure and associate stations to the access point, (iv) launch and stop traffic sessions between stations and the AP.
The WiSHFUL controller executes the logic for controlling the experiment, where we distinguish two phases: first for tuning parameters of a radio program,
second for switching between radio programs. During the first phase, nodes run a CSMA radio program (enabled by default).
Controlling the traffic flows between nodes we generate several congestion states for the network. The WiSHFUL controller dynamically tunes contention
windows on nodes according to the congestion state of the network. This distributed logic runs in all nodes and relies on local observations of the channel
statistics, than takes decisions that are applied locally on nodes.
This local logic is called CW optimum because it is backward compatible with legacy 802.11 nodes. Each node receive the number of network nodes
and calculates an optimal (deterministic) value of contention window.
This logic does not implement an exponential backoff and defines a custom function in the WiSHFUL controller.
To demonstrate benefits of this approach, the number of active traffic flows is incremented. During the experiment, the wishful controller monitors
the network congestion state and when the number of actives flows overcomes a given threshold, it calculates TDMA parameters for the scenario
(number of slots in a TDMA frame, and slot duration) the numbers of nodes, and switches the access scheme on all nodes from CSMA to TDMA. From then
on the experiment reaches its phase two.
In phase two, the number of traffic flows is so high that performances are compromised and tuning the contention window is not sufficient to recover.
The WiSHFUL controller updates the radio program to TDMA, taking a global decision that is enforced in parallel on all nodes. The WiSHFUL controller
requires information about the nodes involved in the experiment.
This is taken via the interface to the experiment controller, currently implemented as a csv file containing node attributes.
The interface between WiSHFUL controller and Experiment controller, provided by a csv file (./testbed_nodes.csv), to store testbed nodes information,
WiSHFUL controller reads node activity to enable the experiment logic

Experiment starting How To

### 1. Experiment nodes registration
Fill the testbed_node.csv with the node present in the testbed. For each node is needed reporting ip, host, name and role in a csv format.
Head example of testbed_node.csv:

ip,hostname,role,platform,traffic

10.163.8.26,alix2,AP,WMP,0
10.163.8.44,alix5,STA,WMP,0

### 2. Starting slave agents
Start the agent on each node to be controlled.

```
./showcase3_agent --config controller_config.yaml
#run with -v for debugging
```

### 3. Starting the testbed controller

The testbed controller has to be started on the testbed server. To run it, user has to execute command:

```
./showcase3_testbed_controller --config controller_config.yaml
#run with -v for debugging
```

### 4. Starting the experiment controller

The experiment controller has to be started on the testbed server. To run it, user has to execute command:

```
./showcase3_experiment_controller --config controller_config.yaml
#run with -v for debugging
```

NB:
In order to setup the testbed and move all relevant files on nodes, the directory wmp_helper contains two bash script:
1)  sync_date.sh that performs the time syncronization of the network nodes.
2)  deploy_upis.sh that performs the files syncronization
Finally the showcase provides a python visualization tool to plot some testbed relevant result in real time, you can run it with the following command:

``
on the testbed server

python showcase_visualizer.py
```