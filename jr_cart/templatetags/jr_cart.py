from django import template
#from jewelry_retail.data_storage.models import 
import datetime

register = template.Library()

def add_to_cart(item):
    link = "/cart/add"+item.get_absolute_url()
    return {"link": link}

register.inclusion_tag("jr_cart_add_to_cart.html")(add_to_cart)


def cart_count(request):
    cart_item_count = len(request.session.get('cart', []))
    cart_item_pricetotal = 0
    for item in request.session.get('cart', []):
        cart_item_pricetotal += item.price
    return {"cart_item_count": cart_item_count, "cart_item_pricetotal": cart_item_pricetotal}

register.inclusion_tag("jr_cart_top_menu.html")(cart_count)