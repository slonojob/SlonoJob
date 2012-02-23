from django.conf.urls.defaults import *

from .settings import MEDIA_ROOT

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    (r'^$', "slono_job.views.index"),

    (r'^user/(?P<user_id>\d+)/$', "slono_job.views.user_history"),

    (r'^resources/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    (r'^(static|img|js|css)/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
)
