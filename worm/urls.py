from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Worm.views.home', name='home'),
    # url(r'^Worm/', include('Worm.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    url(r'^$', 'wobject.views.empty'),

    url(r'worm/v1/wobjects/(?P<name>[A-Za-z0-9_-]+)$', 'wobject.views.main'),
    url(r'worm/v1/wobjects/(?P<name>[A-Za-z0-9_-]+)/(?P<id>[0-9]+)$', 'wobject.views.main'),
    url(r'worm/v1/wobjects/(?P<name>[A-Za-z0-9_-]+)?where=(?P<where>[A-Za-z0-9_-]+)$', 'wobject.views.main'),

)
