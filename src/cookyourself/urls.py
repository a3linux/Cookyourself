from django.conf.urls import url

import cookyourself.views

urlpatterns = [
    url(r'^$', cookyourself.views.index, name='index'),
    url(r'^loadmore$', cookyourself.views.loadmore, name='loadmore'),
    url(r'^dish/(?P<id>\d+)$', cookyourself.views.dish, name='dish'),
    url(r'^shoppinglist$', cookyourself.views.shoppinglist, name='shoppinglist'),
    url(r'^recommendation$', cookyourself.views.recommendation, name='recommendation'),
    url(r'^profile/(?P<id>\d+)$', cookyourself.views.profile, name='profile'),
    url(r'^add_ingredient/(?P<id>\d+)$', cookyourself.views.add_ingredient, name='add_ingredient'),
]
