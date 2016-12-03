Team 205  Cookyourself   Team member: yulunt, yunpengx, wennad

The link to our deployed web site:   http://54.244.78.192/

Description of features and implementations:

features

base:  templates/base.html, 
-base style of website
-navbar and search input on each page
-facebook login and logout
-footer

Related API:
Facebook API

search:
-search recipe based on input, according to dish name and description 

cookyourself/search_indexes.py
templates/search

Related API:
1. haystack -django search API
2. whoosh   -search engine

main:
-dynamically load more recipes from crawler
 using React.js
-filter based on styles, times, and pupolarity
-all dishes'images in uniform size
 using HTML5 canvas

Crawler:
cookyourself/crawler.py 
-Recipe(ingredients, description, instruction...) from allrecipe.com
 
cookyourself/periodic.py
-Periodically craw contents for websites.
-Unit conversion from www.conversion.com

cookyourself/amazon.py
-Price from CUS, Dollar General, Amazon

cookyourself/youtube.py
-Tutorial video based on recipe's name

cookyourself/parser.py
-Parse data from crawler using regular expression
-ntlk Porterstemmer: conversion between singular and plural nouns.

Related packages and API:
1. ntlk-parser
2. requests -crawler
3. selenium -crawler
4. google-api-python-client -youtube
5. crontab -crawler-periodic
6. Amazon product advertising API -Amazon price
7. Beautiful soup -parse html

dish:
-display recipe information
-upvote
-login user can save recipe to profile 
-login user can add ingredients to shopping list
-recipe tutorial video 
-make comments and update in real time

profile:
-display user info from Facebook
-Favorite dishes
-Message Board

shoppinglist:
-display ingredients in shopping list and amount in gram and price
-calculate total price of the list
-send email or print as a pdf of the list to user
-find the nearest store based on user's input, default map centers at Pittsburgh.

PDF generation:
pdfgen.py 
Related API: reportlab

Nearest store:
Google map API

recommendation
-recommend dishes randomly and change 
