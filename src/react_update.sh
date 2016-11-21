#!/bin/bash

echo "react update script"
rm -rf assets/bundles/main-*
rm -rf cookyourself/static/bundles/main-*
./node_modules/.bin/webpack --config webpack.config.js
cp -r assets/bundles cookyourself/static/
# for local test
#./manage.py runserver
# for server update
sudo systemctl restart apache2
