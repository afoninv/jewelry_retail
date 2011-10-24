from django.conf.urls.defaults import patterns, include, url
from jewelry_retail.jr_cart.views import cart, cart_remove, cart_clear, cart_order, cart_help

urlpatterns = patterns("",
    (r'^$', cart),
    (r'^remove/(?P<item_number>\d+)/$', cart_remove),
    (r'^clear/$', cart_clear),
    (r'^order/$', cart_order),
    (r'^help/$', cart_help),

)