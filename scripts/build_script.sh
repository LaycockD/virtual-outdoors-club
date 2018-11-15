#!/bin/bash
ssh -i /tmp/key_outdoors.pem ubuntu@199.116.235.142 <<EOF
    source outdoorsclubenv/bin/activate
    cd virtual-outdoors-club
    pkill -f agent
    eval "$(ssh-agent -s)"
    pwd
    ssh-add ../.ssh/deploy_rsa
    ssh-add -l
    git checkout ssh-encryption
    git pull
    pkill -f npm
    pkill -f node
    pkill -f manage.py
    rm -rf ./dist
    mkdir dist
    mv tmp/* dist
    rm -rf tmp
    pip install -r requirements.txt
    nohup python ./src/django/manage.py process_tasks &
    nohup node server.js & disown
    nohup python ./src/django/manage.py runserver 0.0.0.0:8000 &
    exit 0 && exit
EOF