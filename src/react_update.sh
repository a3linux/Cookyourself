#!/bin/bash

echo "react update script"
rm -rf assets/bundles/main-*
rm -rf cookyourself/static/bundles/main-*
./node_modules/.bin/webpack --config webpack.config.js
cp -r assets/bundles cookyourself/static/
name=`whoami`
if [ "$name" == "ubuntu" ]
then
    sudo systemctl restart apache2
else
./manage.py runserver
fi
