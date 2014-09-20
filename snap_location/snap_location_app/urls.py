from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^test/', views.test),
    url(r'^add_user/', views.add_user),
    url(r'^add_relationship/', views.add_relationship),
    url(r'^friends/', views.show_friends),
)
