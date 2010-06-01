from django.conf.urls.defaults import *

from views import home, all_tags, list_tags, search, put, file_info, get, remove

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

    #List
    (r'^list/$', list_tags),

    #Search
    (r'^search/$', search),

    #Put
    (r'^put/$', put),

    #File
    (r'^file/(?P<file_hash>\w+)$', file_info),

    #Get
    (r'^get/(?P<file_hash>\w+)$', get),

    #Remove
    (r'^remove/(?P<file_hash>\w+)$', remove),
)
