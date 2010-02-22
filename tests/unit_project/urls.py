from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # reverse url lookups
    (r'^', include('mypage.pages.urls')),
)

