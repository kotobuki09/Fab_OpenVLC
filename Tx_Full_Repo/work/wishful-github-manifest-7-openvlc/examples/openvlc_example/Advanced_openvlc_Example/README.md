WiSHFUL WMP advanced tutorial
=============================

For any information or issue, please contact Domenico Garlisi at domenico.garlisi@cnit.it

The goal of this experiment is to create an advance example tutorial for the WiSHFUL framework and the UPI functions usage. 

In this experiment we demonstrate how 

We want to demonstrate how the WISHFUL UPI can be exploited for:
i) Create a network topology with five nodes, an Access Point (AP) and four connected station (STA):

ii) Implement a control program that implements the 

iii) Deploy and run the local control program from controller node to the testbed nodes;

In order to implement the experiment, we run a controller program, or WiSHFUL controller, on a PC connected through
ethernet links to all nodes, and a common agent program in any node.
The controller program permits to: (i) discovery network nodes, (ii) install the execution environment, (iii) create the
BSS infrastructure and associate stations to the access point. In additional, the WiSHFUL controller executes the logic
for controlling the experiment, where we distinguish two phases: first deploy and run the control program on testbed nodes
second ....

For running this experiment, we use two different python scripts: the first script is responsible of network configuration, 
AP activation and station associations (openvlc_testbed_controller); the second script is the most relevant one and 
implements the Global Control Program on top of the WiSHFUL global MCE (openvlc_experiment_controller), which includes 
the metamac_local_control_program that is sent to the local controller of each node.

Below, you can find a step by step how-to to run this example in tesbed nodes, where we will run the WiSHFUL agent, 
and a server to controll them where we will run the WiSHFUL controller. In order to setup the testbed and move all relevant files 
on nodes, the experiment directory contains four additional directory to collect different data, programs and bash scripts
able to provide more functionality to the user
    1) wmp_helper : contains functions to perform node configuration and data showcase analysis, specially the script
     sync_date.sh performs the time syncronization of the network nodes and the script deploy_upis.sh performs the files 
     synchronization;
   
     
### Experiment nodes selection and interface configuration
The file testbed_nodes.csv has been used to set the experiment nodes and the relative information information. For each node 
is needed reporting ip, hostname, role and platform. How reported below 

ip,hostname,role,platform,traffic
10.8.8.102,bg02,AP,wmp,0
10.8.8.103,bg03,STA,wmp,0


### WORKING ON 
        clone on your directory the WiSHFUL project repository:
             follow the user installation How To present at link: https://github.com/wishful-project/manifests
             
### 1. Get the experiment code, deploy it on nodes, and run the WiSHFUL controller on SERVER3
    SHELL 1 - WiSHFUL CONTROLLER :
        connect to controller PC
            ssh 
          
        move in the experiment directory
            cd examples/Advanced_openvlc_Example
 
            cd wmp_helper
            
        deploy framework on alixnodes
            sh deploy_upis.sh bg02,bg03

        sync nodes time:
            sh sync_date.sh bg02,bg03
            cd ..

### 3. Connect on bg0x agent nodes and run the WiSHFUL agent
    SHELL 2  -  bg02 ( node password  : ) :

        connect to the bg02
            ssh root@bg02

        move on the experiment directory
            cd wishful-github-manifest/examples/Advanced_openvlc_Example

        start agent
            chmod +x openvlc_agent
            python3 openvlc_agent --config agent_config.yaml (#run with -v for debugging)

    
    SHELL 3  - bg03 ( node password  : ) :

        connect to the bg03
            ssh root@bg03

        move on the experiment directory
            cd wishful-github-manifest/examples/Advanced_openvlc_Example

        start agent
            chmod +x openvlc_agent
            python3 openvlc_agent --config agent_config.yaml (#run with -v for debugging)

### 4. Start controller on SERVER3
    python3 openvlc_testbed_controller --config controller_config.yaml
        
    python3 openvlc_experiment_controller --config controller_config.yaml (sudo apt-get install python3-matplotlib)


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
    
## Acknowledgement
The research leading to these results has received funding from the European
Horizon 2020 Programme under grant agreement n645274 (WiSHFUL project).
