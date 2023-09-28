DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

WISHFUL_PATH=${DIR%/*/*/*}
OBSS_PATH=${DIR%/*}

AD_ADDRESS='172.16.16.9'

if [ -z "$1" ]
then
	echo "AD_ADDRESS="$AD_ADDRESS
else
	AD_ADDRESS=$1
	echo "AD_ADDRESS="$AD_ADDRESS
fi

source $WISHFUL_PATH/dev/bin/activate
cd $OBSS_PATH
./controller --config ./configs/controller1_config.yaml --ad_address=$AD_ADDRESS
cd ..
