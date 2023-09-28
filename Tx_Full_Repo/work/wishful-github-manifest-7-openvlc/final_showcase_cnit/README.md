Wishful final showcase
============================

### Showcase Phases

Only 1 Administrative Domain present with multiple Wi-Fi deployments to enable the use of the Wi-Fi air time management type of showcases if needed. TUB.e
    Phase 1: LTE added as interferer, CNIT.d (if blank subframes are enabled) , TUB.b, IMEC.a
    Phase 2: (LTE WiSHFUL enabled added, LTE interferer removed) LTE added in 1st AD. (LTE-WIFI coexistence)  TUB.d , CNIT.d, (if collaboration challenge exist)
Phase 3: ADD 2nd Second AD.
    First AD IMEC ZB, 2nd AD TCD virtualized OFDM based networks (frequency separation ? cooperation on the 2.4 GHz band,  blacklisting) IMEC.a, TCD.b

![alt text](https://github.com/wishful-project/final_showcase/blob/master/final-showcase-architecture.jpg)

### Showcase Architecture

The repository is organized with a different directory for each solution, moreover there are three additional directories, solution_global controller, showcase_GUI and lib.


### How work the solution global controller

The paradigm of communication between a generic solution and the solution global controller has two different phases.
    Phase 1: The solutions use a request/reply format to register them on solution global controller ( the following information
    are required for the registration procedure: Name; monitorList; commandList; eventList;).
    Phase 2: The solutions use a request/reply format to send monitor information and event detected to the solution global controller.
    The solution global controller uses the PUB/SUB to send command to the solutions.

The solutions are registered in the solutionCompatibilityMatrix map, we add also eventually conflict between the solutions in order to
use this information in the main logic of the solution global controller. The main logic of the solution global controller waiting for
receiving a monitor/event report, the solution global controller checks the solution compatibility matrix, in order to understand eventually conflict,
and send update/command to solutions. Example: when it receives the report of detecting interference (LTE),
sends activation command to solution TDMA cross interference, if not conflict are detected.

![alt text](https://github.com/wishful-project/final_showcase/blob/master/solution-global-controller-main-logic.jpg)

### how-to showcase activation on portable testbed

### 1. involved nodes 
172.16.16.12 nuc12 --> AD controller + wifi controller + lte controller + USRP channel acquire + webui
172.16.16.11 nuc11 --> LTE ENB
172.16.16.6 nuc6   --> LTE UE

### 2. run the showcase 
Start the AD controller (SHELL 1):

    ssh dgarlisi@nuc12
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/ad_controller/
    python3 ./controller
    
in the shell 1 you can see the registered networks and you can send command to networks, 
you can follow the command line menu to activate wifi/LTE traffic, afterwards, 
the AD controller will receive the monitor report messages and send them ot the webui.

Start CNIT_WIFI_NETWORK  (SHELL 2) (need AD controller activated):

     ssh dgarlisi@nuc12
     cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/network_wifi/solution_wifi_ct/
     ex -sc $"%s/\r$//e|x" start_wifi_network.sh
     bash start_wifi_network.sh

Start CNIT_LTE_NETWORK  (SHELL 3) (need AD controller activated):

    ssh dgarlisi@nuc12
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/network_lte/solution_lte_ct/
    ex -sc $"%s/\r$//e|x" start_lte_network.sh
    bash start_lte_network.sh

Start INTERFERENCE_DETECTION  (SHELL 4) (need AD controller activated):

    ssh dgarlisi@nuc11
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/spectrum_monitoring_service/solution_interference_detection/
    sudo python3 controller --config controller_cfg_nuc11.yaml --nodes node_info.txt

Start USRP channel trace visualizer on web portal  (SHELL 5):

    ssh dgarlisi@nuc12
    cd /groups/portable-ilabt-imec-be/wish/cnit/pyUsrpTrackerWishfulWebPortal
    sudo bash run_usrp.sh 11

you can see the trace via web browser at address : http://172.16.16.12/WishfulWebPortal/only_usrp.html

Start graphical interface (SHELL 6):

    ssh dgarlisi@nuc12
    cd /groups/portable-ilabt-imec-be/wish/cnit/wishful-github-manifest-7/final_showcase/webui/
    bokeh serve --allow-websocket-origin=*:5006 wishful
    
        (sudo pipenv shell bokeh serve --allow-websocket-origin="*:5006" wishful) ??

you can see the statistics via web browser at address : http://172.16.16.6:5006/wishful


    #sudo ntpdate -u it.pool.ntp.org

## Acknowledgement

The research leading to these results has received funding from the European
Horizon 2020 Programme under grant agreement n645274 (WiSHFUL project).