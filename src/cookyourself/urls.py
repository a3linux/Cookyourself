from django.conf.urls import url

import cookyourself.views

urlpatterns = [
    url(r'^$', cookyourself.views.index, name='index'),
    url(r'^loadmore/(?P<id>\d+)$', cookyourself.views.loadmore, name='loadmore'),
    url(r'^dish/(?P<id>\d+)$', cookyourself.views.dish, name='dish'),
    url(r'^shoppinglist$', cookyourself.views.shoppinglist, name='shoppinglist'),
    url(r'^recommendation$', cookyourself.views.recommendation, name='recommendation'),
    url(r'^change_recommend$', cookyourself.views.change_recommend),
    url(r'^profile/(?P<id>\d+)$', cookyourself.views.profile, name='profile'),
    url(r'^add_ingredient/(?P<iid>\d+)$', cookyourself.views.add_ingredient, name='add_ingredient'),
    url(r'^del_ingredient$', cookyourself.views.del_ingredient, name='del_ingredient'),
    url(r'^upvote_dish$', cookyourself.views.upvote_dish),
    url(r'^save_dish$', cookyourself.views.save_dish),
    url(r'^get_shoppinglist$', cookyourself.views.get_shoppinglist, name='get_shoppinglist'),
    url(r'^add_user$', cookyourself.views.add_user, name='add_user'),
    url(r'^logout_user$', cookyourself.views.logout_user, name='logout_user'),
    url(r'^create_post$', cookyourself.views.create_post, name='create_post'),
    url(r'^update_posts/?$', cookyourself.views.update_posts),
    url(r'^create_message$', cookyourself.views.create_message, name='create_message'),
    url(r'^update_messages/?$', cookyourself.views.update_messages),
    url(r'^filter/(?P<id>\d+)$', cookyourself.views.filter, name='filter'),
    url(r'^search/', cookyourself.views.filter),
    url(r'^print_list/', cookyourself.views.print_list, name='print_list'),
    url(r'^error$', cookyourself.views.error, name='error'),
]
