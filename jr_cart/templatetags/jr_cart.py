from django import template

register = template.Library()

def cart_summary(request):
    cart_item_count = request.session.get('cart_count')
    cart_item_count = u' (%i)' % cart_item_count if cart_item_count else u''
    return {"cart_item_count": cart_item_count}

def cart_list(request):
    return {'cart_list': request.session.get('cart') or []}

register.inclusion_tag("jr_cart_summary.html")(cart_summary)
register.inclusion_tag("jr_cart_list.html")(cart_list)