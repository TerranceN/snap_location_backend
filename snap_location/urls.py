from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'snap_location.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^snap_location/', include('snap_location.snap_location_app.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
