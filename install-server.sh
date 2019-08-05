#! /usr/bin/env bash

apt update

apt install nginx redis-server postgresql git build-essential


INSTANCE="hive"
USERNAME="sl"
CONFIGPATH="/etc/${INSTANCE}"
CONFIGFILE="${CONFIGPATH}/${INSTANCE}.yml"
DBNAME="${INSTANCE}"
PYTHON=$(which python3.6)
PIP=$(which pip3.6)

curl https://bootstrap.pypa.io/get-pip.py | $PYTHON
useradd -r ${USERNAME}

echo "CREATE USER ${USERNAME}" | sudo -u postgres psql

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


echo "CREATE DATABASE ${DBNAME} OWNER ${USERNAME}" | sudo -u postgres psql


sudo -u ${USERNAME} hive --config-file ${CONFIGFILE} db schema

echo "d /run/${INSTANCE} 0755 ${USERNAME} ${USERNAME} -" > /etc/tmpfiles.d/${INSTANCE}.conf


echo "
import os
from hive import SharedLists

app = SharedLists()
app.configure(filename='${CONFIGFILE}')
app.initialize_orm()

" > ${CONFIGPATH}/wsgi.py


echo "
[Unit]
Description=SharedLists REST API
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

openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/sl-selfsigned.key -out /etc/ssl/certs/sl-selfsigned.crt
openssl dhparam -out /etc/ssl/certs/sl-dhparam.pem 2048

echo "
upstream ${INSTANCE}_api {
    server unix:/run/${INSTANCE}/${INSTANCE}.socket fail_timeout=1;
}


server {
    listen 443 ssl http2;
	

    location / {
      proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
      proxy_redirect off;
      proxy_pass http://${INSTANCE}_api;
    }

	ssl_certificate /etc/ssl/certs/sl-selfsigned.crt;
	ssl_certificate_key /etc/ssl/private/sl-selfsigned.key;
	ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
	ssl_prefer_server_ciphers on;
	ssl_ciphers \"EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH\";
	ssl_ecdh_curve secp384r1;
	ssl_session_cache shared:SSL:10m;
	ssl_session_tickets off;
	ssl_stapling_verify on;
	add_header Strict-Transport-Security \"max-age=63072000; includeSubdomains\";
	add_header X-Frame-Options DENY;
	add_header X-Content-Type-Options nosniff;

	ssl_dhparam /etc/ssl/certs/sl-dhparam.pem;

}
" > /etc/nginx/sites-available/${INSTANCE}.conf
ln -s /etc/nginx/sites-available/${INSTANCE}.conf /etc/nginx/sites-enabled/${INSTANCE}.conf
service nginx restart

