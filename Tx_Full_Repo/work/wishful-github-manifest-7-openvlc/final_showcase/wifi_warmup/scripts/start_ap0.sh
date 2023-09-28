DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

WISHFUL_PATH=${DIR%/*/*/*}
OBSS_PATH=${DIR%/*}

source $WISHFUL_PATH/dev/bin/activate
cd $OBSS_PATH
./agent --config ./configs/ap0_config.yaml
cd ..
