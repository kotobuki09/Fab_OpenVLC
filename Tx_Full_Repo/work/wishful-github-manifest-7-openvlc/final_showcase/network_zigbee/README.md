Wishful FINAL SHOWCASE network_zigbee
==========================================

0. Change to wishful user (password wishful)

        su wishful 

1. Flash the sensor nodes (ONLY NECESSARY if zolertia remotes were not flashed with this image before)

Navigate to the udp example directory:

        cd ~/contiki/examples/wishful-ipv6/taisc/udp/

Execute the make command (X is the node id)
        
        make TARGET=zoul udp-example.upload NODE_ID=1
        
2. run the agent:

Activate the virtual environment:

        source ./dev/bin/activate
        
Navigate to the zigbee network directory:

        cd final_showcase/network_zigbee

Start the agent:

        python agent.py --config config/portable/agent_config.yaml

3. run the global controller:

Activate the virtual environment:

        source ./dev/bin/activate

Go to the zigbee network directory:

        cd final_showcase/network_zigbee

Start the global controller:

        python global_controller.py --config config/portable --solution_controller "AD_CONTROLLER_IP"
