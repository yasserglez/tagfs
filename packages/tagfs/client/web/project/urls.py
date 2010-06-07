from django.conf.urls.defaults import *
from django.views.static import serve
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^tagfs/', include('tagfs.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    
    #App
    (r'^', include('app.urls')),
    
    #Media
    (r'^media/(?P<path>.*)$', serve, dict(document_root=settings.MEDIA_ROOT)),
)
