DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

WISHFUL_PATH=${DIR%/*/*/*/*}
DET_PATH=$WISHFUL_PATH/final_showcase/spectrum_monitoring_service/solution_interference_classifier

AD_ADDRESS='172.16.16.2'

if [ -z "$1" ]
then
	echo "AD_ADDRESS="$AD_ADDRESS
else
	AD_ADDRESS=$1
	echo "AD_ADDRESS="$AD_ADDRESS
fi

source $WISHFUL_PATH/dev/bin/activate
cd $DET_PATH
./wiplus_controller --config ./configs/wiplus_config.yaml --ad_address=$AD_ADDRESS
cd ..
