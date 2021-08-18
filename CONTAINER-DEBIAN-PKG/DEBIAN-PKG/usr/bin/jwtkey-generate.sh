#!/bin/bash

set -e

cd /tmp;

openssl genrsa -out jwt-key 2048;
openssl rsa -in jwt-key -pubout > jwt-key.pub;

sed -i -e ':a;N;$!ba;s|\n|§|g' jwt-key.pub;
sed -i -e ':a;N;$!ba;s|"publicKey.*,|"publicKey": '\'\'\'"$(echo $(cat jwt-key.pub))"\'\'\','|g' /var/www/aaa/aaa/settings_jwt.py;

sed -i -e ':a;N;$!ba;s|\n|§|g' jwt-key;
sed -i -e ':a;N;$!ba;s|"privateKey.*}|"privateKey": '\'\'\'"$(echo $(cat jwt-key))"\'\'\''\n}|g' /var/www/aaa/aaa/settings_jwt.py;
sed -i -e ':a;N;$!ba;s|§|\n|g' /var/www/aaa/aaa/settings_jwt.py;

rm jwt-key*

exit 0
