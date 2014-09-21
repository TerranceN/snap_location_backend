from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^test/', views.test),
    url(r'^add_user/', views.add_user),
    url(r'^add_relationship/', views.add_relationship),
    url(r'^friends/', views.show_friends),
    url(r'^file_upload_test/', views.file_upload_test),
    url(r'^upload_image/', views.upload_file),
    url(r'^get_users/', views.get_users),
    url(r'^get_gamedata/', views.get_gamedata),
    url(r'^get_images/', views.get_images),
    url(r'^get_relationships/', views.get_relationships),
    url(r'^push_image_location/', views.push_image_location),
    url(r'^upload_game_round/', views.upload_game_round),
    url(r'^guess_location/', views.guess_location),
    url(r'^make_user/', views.make_user),
    url(r'^make_relationship/', views.make_relationship),
    url(r'^next_image/', views.get_image),
    url(r'^get_profile/', views.get_profile),
)
