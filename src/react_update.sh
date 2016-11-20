#!/bin/bash

echo "react update script"
rm -rf assets/bundles/main-*
./node_modules/.bin/webpack --config webpack.config.js
cp -r assets/* cookyourself/static/
# for local test
#./manage.py runserver
# for server update
#sudo systemctl restart apache2
