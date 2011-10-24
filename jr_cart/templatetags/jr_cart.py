from django import template

register = template.Library()

def cart_count(request):
    cart_item_count = request.session.get('cart_count', 0)
    cart_item_pricetotal = request.session.get('cart_price', 0)
    return {"cart_item_count": cart_item_count, "cart_item_pricetotal": cart_item_pricetotal}

register.inclusion_tag("jr_cart_top_menu.html")(cart_count)