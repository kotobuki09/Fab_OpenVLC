DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

WISHFUL_PATH=${DIR%/*/*/*}
AD_PATH=$WISHFUL_PATH/final_showcase/ad_controller

source $WISHFUL_PATH/dev/bin/activate
cd $AD_PATH
python ./controller
cd ..
