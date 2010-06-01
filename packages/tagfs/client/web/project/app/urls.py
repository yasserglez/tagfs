from django.conf.urls.defaults import *

from views import home, all_tags, put

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

    #Home
    (r'^$', home),

    #All tags
    (r'^all_tags/$', all_tags),

    #Search
    (r'^search/$', home),

    #Upload
    (r'^put/$', put),
)
