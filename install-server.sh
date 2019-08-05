#! /usr/bin/env bash

apt update

apt install nginx redis-server postgresql git build-essential


INSTANCE="hive"
USERNAME="hive"
CONFIGPATH="/etc/${INSTANCE}"
CONFIGFILE="${CONFIGPATH}/${INSTANCE}.yml"
DBNAME="${INSTANCE}"
PYTHON=$(which python3.6)
PIP=$(which pip3.6)

curl https://bootstrap.pypa.io/get-pip.py | $PYTHON
useradd -r ${USERNAME}

echo "CREATE USER ${USERNAME}" | sudo -Hu postgres psql

$PIP install .


mkdir -p $CONFIGPATH
echo "
db:
  url: postgresql+psycopg2://${USERNAME}:@/${DBNAME}

jwt:
  secret: 5cbc17ea278f445b-89f2eca967de3c17 
  algorithm: HS256
  max_age: 31536000  # 1 Year

" > ${CONFIGFILE}


echo "CREATE DATABASE ${DBNAME} OWNER ${USERNAME}" | sudo -Hu postgres psql


sudo -u ${USERNAME} hive --config-file ${CONFIGFILE} db schema

echo "d /run/${INSTANCE} 0755 ${USERNAME} ${USERNAME} -" > /etc/tmpfiles.d/${INSTANCE}.conf


echo "
import os
from hive import Hive

app = Hive()
app.configure(filename='${CONFIGFILE}')
app.initialize_orm()

" > ${CONFIGPATH}/wsgi.py


echo "
[Unit]
Description=Hive REST API
After=network.target

[Service]
PIDFile=/run/${INSTANCE}/pid
User=${USERNAME}
Group=${USERNAME}
ExecStart=/usr/local/bin/gunicorn --workers 1 --bind unix:/run/${INSTANCE}/${INSTANCE}.socket --pid /run/${INSTANCE}/pid --chdir ${CONFIGPATH} wsgi:app
ExecReload=/bin/kill -s HUP \$MAINPID
ExecStop=/bin/kill -s TERM \$MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/${INSTANCE}.service

systemd-tmpfiles --create
systemctl daemon-reload
systemctl enable ${INSTANCE}.service
service ${INSTANCE} start


echo "
upstream ${INSTANCE}_api {
    server unix:/run/${INSTANCE}/${INSTANCE}.socket fail_timeout=1;
}


server {
    listen 443 ssl http2;

    location ~ ^/apiv1/(?<url>.*) {
      proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
      proxy_redirect off;
      proxy_pass http://${INSTANCE}_api/\$url;
    }
}
" > /etc/nginx/sites-available/${INSTANCE}.conf
ln -s /etc/nginx/sites-available/${INSTANCE}.conf /etc/nginx/sites-enabled/${INSTANCE}.conf
service nginx restart

