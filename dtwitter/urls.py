from django.conf.urls.defaults import *

urlpatterns = patterns('dtwitter.views',
    (r'^connect/$', 'connect'),
    (r'^callback/$', 'callback'),
    (r'^logout/$', 'logout'),
)

