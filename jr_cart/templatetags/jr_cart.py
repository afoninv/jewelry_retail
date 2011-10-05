from django import template
#from jewelry_retail.data_storage.models import 
import datetime

register = template.Library()

def add_to_cart(item, j_type_eng):
    link = "/cart/add/"+j_type_eng+u'/'+unicode(item)
    return {"link": link}

register.inclusion_tag("jr_cart_add_to_cart.html")(add_to_cart)