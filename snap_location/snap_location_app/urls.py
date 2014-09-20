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
    url(r'^guess_location/', views.guess_location),
    url(r'^next_image/', views.get_image),
)
