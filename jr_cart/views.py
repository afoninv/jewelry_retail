from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect

from jewelry_retail.data_storage.models import Article, Suite

def cart(request):
    request.session['cart'] = request.session.get('cart', [])
    return render_to_response("jr_cart.html", {'items': request.session['cart']})

def cart_add(request, j_type=None, j_id=None):
# do input sanitization

    if j_type == u'suite': 
        item = Suite.objects.get(id=j_id)
        item.j_type_eng = u'suite'
    else: 
        item = Article.objects.get(id=j_id)
        item.j_type_eng = unicode(item.j_type.name_eng)

    items = request.session.get('cart') or []
    items.append(item)
    request.session['cart'] = items

    return HttpResponseRedirect("/cart/")

def cart_clear(request):
    request.session['cart'] = []
    return render_to_response("jr_cart.html")

def cart_remove(request, j_type=None, j_id=None):
# do input sanitization

    if j_type == u'suite': 
        item = Suite.objects.get(id=j_id)
        item.j_type_eng = u'suite'
    else: 
        item = Article.objects.get(id=j_id)
        item.j_type_eng = unicode(item.j_type.name_eng)    

    items = request.session.get('cart', [])
    if item in items: 
        items.remove(item)
        request.session['cart'] = items
    return HttpResponseRedirect("/cart/")