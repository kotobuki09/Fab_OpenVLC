METAMAC howto

### WORKING ON TTILAB


    #move files on controller
    rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ./wishful-github-manifest-7/  -e ssh lab.tti.unipa.it:~/wishful-github-manifest-7/

    rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ./wishful-github-manifest-7/  -e ssh 10.8.7.2:~/wishful-github-manifest-7/

    rsync -avz  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ./wishful-github-manifest-7/  -e ssh 10.8.7.2:~/wishful-github-manifest-7/

    #connect to controller PC
    ssh domenico@lab.tti.unipa.it
    cd wishful-github-manifest-7/examples/Get_Started_Examples/Advanced_WMP_Example/

    ssh domenico@10.8.7.2
    cd wishful-github-manifest-7/examples/Get_Started_Examples/Advanced_WMP_Example/
    source ./dev/bin/activate

    cd wmp_helper/
    deploy framework on alixnodes
        cat deploy_upis.sh | tr -d '\r' >> deploy_upis_2.sh
        sh deploy_upis_2.sh 10.8.8.102,10.8.8.103
    sync nodes time:
        cat sync_date.sh | tr -d '\r' >> sync_date_2.sh
        sh sync_date_2.sh 10.8.8.102,10.8.8.103

    cd ..

#start agent
python3 metamac_agent --config agent_config.yaml
python3 metamac_agent --config agent_config_ap.yaml

#start controller on server
    #replace nodes configuraiton if needed
    10.8.8.102,alix02,AP,wmp,0
    10.8.8.104,alix04,STA,wmp,0

 source ./dev/bin/activate

python3 metamac_testbed_controller --config controller_config_nova.yaml
python3 metamac_testbed_controller --config controller_config_ttilab.yaml
python3 metamac_testbed_controller --config controller_config_warm.yaml


    #test network
    ping 192.168.3.102




PER MARCO, da questo punto in poi c'è la fase di controller di esperimento. La vediamo insieme
python3 metamac_experiment_controller --config controller_config_nova.yaml
python3 experiment_controller_v0 --config controller_config_ttilab.yaml

#forward command
ssh -L 8301:127.0.0.1:8301 domenico@lab.tti.unipa.it -v
ssh -L 8300:127.0.0.1:8300 domenico@lab.tti.unipa.it -v

#start USRP
    ssh lab.tti.unipa.it
    ssh clapton.local
    sudo /home/domenico/work/CREW_FINAL_DEMO/pyTrackers/pyUsrpTracker/run_usrp.sh 6
    ssh -L 8310:10.8.9.3:80 domenico@lab.tti.unipa.it
    http://127.0.0.1:8310/crewdemo/plots/usrp.png
    python metamac_visualizer.py