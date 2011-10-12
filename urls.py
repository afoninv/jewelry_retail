from django.conf.urls.defaults import patterns, include, url
from jewelry_retail.views import mainpage, catalogue, catalogue_view, id_view, catalogue_search

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'jewelry_retail.views.home', name='home'),
    # url(r'^jewelry_retail/', include('jewelry_retail.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),



    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),


    ('^$', mainpage),
    ('^catalogue/$', catalogue),
    ('^catalogue/search/$', catalogue_search),
    ('^catalogue/(?P<j_type>\w+)/$', catalogue_view),
    ('^catalogue/(?P<j_type>\w+)/(?P<j_id>\d+)/$', id_view),
    (r'^cart/', include("jewelry_retail.jr_cart.urls")),


    (r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'c:/python26/jewelry_retail/images/'}),

)
