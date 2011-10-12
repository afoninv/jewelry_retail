from django.conf.urls.defaults import patterns, include, url
from jewelry_retail.jr_cart.views import cart, cart_add, cart_remove, cart_clear, cart_message, cart_order, cart_help

urlpatterns = patterns("",
    (r'^$', cart),
    (r'^add/catalogue/(?P<j_type>\w+)/(?P<j_id>\d+)/$', cart_add),
    (r'^remove/catalogue/(?P<j_type>\w+)/(?P<j_id>\d+)/$', cart_remove),
    (r'^clear/$', cart_clear),
    (r'^message/$', cart_message),
    (r'^order/$', cart_order),
    (r'^order/help/$', cart_help),

)