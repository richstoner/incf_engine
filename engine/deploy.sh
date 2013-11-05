#!/bin/sh

str="ansible-playbook ops/deploy.yml -i ops/hosts"

if [[ $1 = "--fast" ]]; then
    echo "Performing fast deploy"
    str="${str} --extra-vars "fast_deploy=true""
elif [[ $1 = "--help" ]]; then
    echo "Usage: deploy.sh [deploy-type]"
    echo "  --fast    Do a fast deploy where only the code is updated and the app is restarted"
    echo "  --help    This message"
    exit
else
    echo "Performing normal deploy"
fi

exec $str
