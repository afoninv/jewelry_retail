from django.conf.urls.defaults import patterns, include, url
from jewelry_retail.jr_cart.views import cart, cart_add, cart_remove, cart_clear

urlpatterns = patterns("",
    (r'^$', cart),
    (r'^add/(?P<j_type>\w+)/(?P<j_id>\d+)/$', cart_add),
    (r'^remove/(?P<j_type>\w+)/(?P<j_id>\d+)/$', cart_remove),
    (r'^clear/$', cart_clear),
)